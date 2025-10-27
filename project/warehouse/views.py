from decimal import Decimal

from django.contrib.auth.decorators import permission_required, login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect

from project.views import ProjectBaseListView

from .forms import AcceptanceForm, NewWriteOffForm
from .models import (
    Acceptance,
    WriteOff,
    Availability,
    Warehouse,
    ProductTransfer,
    WriteOffCause,
)
from contracts.models import Contract

from main.services.menu_info import get_menu_product_composition
from main.models import MenuRequirement

from staff.models import get_staff_by_user

from .services.warehouse_transactions import product_transfer, write_off_from_warehouse


class WarehouseListView(ProjectBaseListView):
    """
    Mixin-ListView для всех ListView складских перемещений
    """

    # TODO: общий template
    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.GET.get("warehouse"):
            queryset = queryset.filter(warehouse=self.request.GET.get("warehouse"))

        if self.request.GET.get("product"):
            queryset = queryset.filter(warehouse=self.request.GET.get("product"))

        return queryset


class AcceptanceListView(WarehouseListView):
    model = Acceptance
    template_name = "warehouse/acceptance.html"


class WriteOffListView(WarehouseListView):
    model = WriteOff
    template_name = "warehouse/write_off.html"


class AvailabilityListView(WarehouseListView):
    model = Availability
    template_name = "warehouse/availability.html"


class ProductTransferListView(ProjectBaseListView):
    model = ProductTransfer
    template_name = "warehouse/transfers.html"


def load_products_for_acceptance(request):
    contract_id = request.GET.get("contract")
    contract = Contract.objects.get(id=contract_id)
    return contract.products.all()


@login_required
@permission_required("warehouse.add_acceptance")
def create_acceptance(request):
    if request.method == "POST":
        products = request.POST.getlist("product")
        volumes = request.POST.getlist("volume")
        warehouse = request.POST["warehouse"]

        for i in range(len(products)):
            form = AcceptanceForm(
                data={
                    "contract": request.POST["contract"],
                    "product": products[i],
                    "volume": volumes[i],
                    "warehouse": warehouse,
                }
            )
            if form.is_valid():
                form.save()  # TODO: перед проверкой проверять, хватит ли денег
            else:  # Если форма не валидная, перезагружается страница и передаётся сообщение об ошибке
                context = {
                    "title": "Принять на склад",
                    "form": form,
                }
                return render(request, "warehouse/create_acceptance.html", context)
        return redirect("/warehouse/acceptance")

    form = AcceptanceForm()
    actual_contracts = Contract.objects.filter(is_actual=True)
    context = {
        "title": "Принять на склад",
        "form": form,
        "actual_contracts": actual_contracts,
    }
    return render(request, "warehouse/create_acceptance.html", context)


@login_required
@permission_required("warehouse.add_acceptance")
def render_acceptance_form(request):
    contract_id = request.GET.get("contract")
    options = Contract.objects.get(id=contract_id).products.all()
    form = AcceptanceForm()
    context = {
        "form": form,
        "contract_id": contract_id,
        "options": options,
    }
    return render(request, "warehouse/partials/acceptance_form.html", context)


@login_required
def add_product_to_acceptance(request):
    contract_id = request.GET.get("contract")
    options = Contract.objects.get(id=contract_id).products.all()
    return render(
        request,
        "warehouse/partials/acceptance_product_form.html",
        {"form": AcceptanceForm(), "options": options},
    )


@login_required
@permission_required("warehouse.add_writeoff")
def create_write_off(request):
    if request.method == "POST":
        user = request.user

        products = request.POST.getlist("product")
        volumes = request.POST.getlist("volume")
        print(f"volumes: {volumes}")
        warehouse = request.POST["warehouse"]
        note = request.POST["note"]
        cause = request.POST["cause"]
        for i in range(len(products)):
            print(f"volume: {volumes[i]}")
            form = NewWriteOffForm(
                data={
                    "product": products[i],
                    "volume": volumes[i],
                    "warehouse": warehouse,
                    "note": note,
                    "cause": cause,
                }
            )

            if form.is_valid():
                print("form is valid")
                form.save()
                print("form saved")
            else:  # TODO: не нравится
                context = {
                    "title": "Списать со склада",
                    "form": form,
                }
                return render(request, "warehouse/create_write_off.html", context)

        return redirect("/warehouse/write_off")
    form = NewWriteOffForm()
    context = {
        "title": "Списать со склада",
        "form": form,
    }
    return render(request, "warehouse/create_write_off.html", context)


def add_product_to_write_off(request):
    return render(
        request, "warehouse/partials/write_off_form.html", {"form": NewWriteOffForm()}
    )


@transaction.atomic
@permission_required("warehouse.add_producttransfer")
def issue_menu(request):
    staff = get_staff_by_user(request.user)
    errors = []
    if request.method == "POST":
        warehouse_from = Warehouse.objects.get(name="Основной")
        warehouse_to = Warehouse.objects.get(name="Кухня")
        menu_requirement_id = request.POST.get("menu_requirement", None)
        menu_requirement = MenuRequirement.objects.get(id=menu_requirement_id)
        if menu_requirement_id:
            menu_products = get_menu_product_composition(menu_requirement)
            for el in menu_products:
                try:
                    product_transfer(
                        warehouse_from=warehouse_from,
                        warehouse_to=warehouse_to,
                        product=el["product"],
                        volume=Decimal(el["volume"] / 1000),
                        staff=staff,
                        note=f"Отпуск продукта по {menu_requirement}",
                    )
                except Exception as e:
                    return HttpResponse(e)
            menu_requirement.is_issued = True
            menu_requirement.save()
            return HttpResponse("Отправлено!")
        else:
            return HttpResponse("Ошибка!")

    return HttpResponse("Ошибка!")


@transaction.atomic
@permission_required("warehouse.add_writeoff")
def cook_menu(request):
    staff = get_staff_by_user(request.user)
    errors = []
    if request.method == "POST":
        warehouse = Warehouse.objects.get(name="Кухня")
        cause = WriteOffCause.objects.get(name="Приготовление блюд")
        menu_requirement_id = request.POST.get("menu_requirement", None)
        menu_requirement = MenuRequirement.objects.get(id=menu_requirement_id)
        if menu_requirement_id:
            menu_products = get_menu_product_composition(menu_requirement)
            for el in menu_products:
                try:
                    write_off_from_warehouse(
                        product=el["product"],
                        volume=Decimal(el["volume"] / 1000),
                        warehouse=warehouse,
                        cause=cause,
                        note=f"Списание продукта по {menu_requirement}",
                    )
                except Exception as e:
                    return HttpResponse(e)
            menu_requirement.is_cooked = True
            menu_requirement.save()
            return HttpResponse("Отправлено!")
        else:
            return HttpResponse("Ошибка!")

    return HttpResponse("Ошибка!")

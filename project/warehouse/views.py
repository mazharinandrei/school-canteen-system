
from django.contrib.auth.decorators import permission_required, login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect

from project.views import ProjectBaseListView
from .exceptions import NotEnoughProductToWriteOff, NotEnoughProductToTransfer

from .forms import AcceptanceForm, NewWriteOffForm
from .models import (
    Acceptance,
    WriteOff,
    Availability,
    ProductTransfer,
)
from contracts.models import Contract


from staff.models import get_staff_by_user

from .services.warehouse_transactions import (
    cook_menu,
    issue_menu,
)


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

    def get_queryset(self):
        return (
            self.model.objects.all()
            .select_related("warehouse")
            .select_related("contract")
            .select_related("product")
            .prefetch_related("staff")
            .prefetch_related("contract__counterparty")
        )


class WriteOffListView(WarehouseListView):
    model = WriteOff
    template_name = "warehouse/write_off.html"

    def get_queryset(self):
        return (
            self.model.objects.all()
            .select_related("warehouse")
            .select_related("product")
            .select_related("cause")
            .prefetch_related("staff")
        )


class AvailabilityListView(WarehouseListView):
    model = Availability
    template_name = "warehouse/availability.html"

    def get_queryset(self):
        return (
            self.model.objects.all()
            .select_related("warehouse")
            .select_related("product")
        )


class ProductTransferListView(ProjectBaseListView):
    model = ProductTransfer
    template_name = "warehouse/transfers.html"

    def get_queryset(self):
        return (
            self.model.objects.all()
            .select_related("warehouse_from")
            .select_related("warehouse_to")
            .select_related("product")
            .prefetch_related("staff")
        )


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
def on_issue_menu_button_click(request):
    errors = []
    try:
        issue_menu(
            created_by=get_staff_by_user(request.user),
            menu=request.POST.get("menu_requirement", None),
            from_warehouse_name="Основной",
        )
    except NotEnoughProductToTransfer as e:
        errors.append(
            f'На складе "{e.warehouse_name}" '
            f'продукта "{e.product_name}" меньше, '
            f"чем планируется переместить на кухню"
        )
    if errors:
        return HttpResponse("\n".join(errors))
    else:
        return HttpResponse("Отправлено!")


@transaction.atomic
@permission_required("warehouse.add_writeoff")
def on_cook_menu_button_click(request):
    errors = []
    try:
        cook_menu(
            menu=request.POST.get("menu_requirement", None),
            created_by=get_staff_by_user(request.user),
        )
    except NotEnoughProductToWriteOff as e:
        errors.append(
            f'На складе "{e.warehouse_name}" продукта "{e.product_name}" меньше, чем планируется списать'
        )
    if errors:
        return HttpResponse("\n".join(errors))
    else:
        return HttpResponse("Отправлено!")

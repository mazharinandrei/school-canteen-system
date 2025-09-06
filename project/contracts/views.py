import os

from django.contrib.auth.decorators import login_required
from django.db.models import ExpressionWrapper, F
from django.forms import FloatField
from django.http import Http404, FileResponse
from django.shortcuts import render, redirect, get_object_or_404

from .forms import ContractForm, CounterpartyForm, ContractFormSet, ContractFileUploadForm
from .models import Contract, Counterparty, ContractComposition
from staff.models import get_staff_by_user


# Create your views here.

@login_required
def render_all_contracts(request):
    contracts = Contract.objects.all().order_by('-date')
    context = {
        "title": "Все договоры",
        "contracts": contracts,

    }
    return render(request, "contracts/all_contracts.html", context)


@login_required
def create_contract(request):
    if request.method == 'POST':

        form = ContractForm(request.POST)

        products = request.POST.getlist("product")
        volumes = request.POST.getlist("total_volume")
        costs = request.POST.getlist("cost")

        staff = get_staff_by_user(request.user)

        data_for_formset = {

            "contractcomposition_set-TOTAL_FORMS": str(len(products)),
            "contractcomposition_set-INITIAL_FORMS": "0",
        }

        for i in range(len(products)):
            data_for_formset[f"contractcomposition_set-{i}-product"] = products[i]
            data_for_formset[f"contractcomposition_set-{i}-total_volume"] = volumes[i]
            data_for_formset[f"contractcomposition_set-{i}-cost"] = costs[i]
        print(data_for_formset)
        formset = ContractFormSet(data_for_formset)


        if form.is_valid() and formset.is_valid():
            contract = form.save(commit=False)
            contract.staff = staff

            contract.save()

            formset.instance = contract

            formset.save()
            return redirect('/contracts/all_contracts')
        else:
            print(form.errors)
            print(formset.errors)
    else:
        form = ContractForm(initial={'staff': get_staff_by_user(request.user)})
        formset = ContractFormSet()
    context = {
        "title": "Добавить договор",
        'form': form,
        'formset': formset,
    }

    return render(request, "contracts/create_contract.html", context)


def render_contract(request, contract_id):
    contract = Contract.objects.get(id=contract_id)

    if request.method == 'POST' and not contract.file:
        form = ContractFileUploadForm(request.POST, request.FILES, instance=contract)
        if form.is_valid():
            form.save()
    else:
        form = ContractFileUploadForm(instance=contract)

    context = {
        "title": contract,
        "contract": contract,
        'form': form if not contract.file else None

    }
    return render(request, "contracts/contract.html", context)


@login_required
def render_counterparties(request):
    counterparties = Counterparty.objects.all()
    context = {
        "title": "Все контрагенты",
        "counterparties": counterparties,
    }
    return render(request, "contracts/all_counterparties.html", context)


@login_required
def create_counterparty(request):
    form = CounterpartyForm()

    if request.method == 'POST':
        form = CounterpartyForm(request.POST)
        if form.is_valid():
            n = form.save()
            return redirect("/contracts/all_counterparties/")
    else:
        context = {
            "title": "Добавить контрагента",
            "form": form,
        }
        return render(request, "contracts/create_counterparty.html", context)


@login_required
def add_product_to_contract(request):
    return render(request, 'contracts/partials/add_product_to_contract_form.html',
                  {'formset': ContractFormSet()})

def render_counterparty(request, counterparty_id):
    counterparty = Counterparty.objects.get(id=counterparty_id)
    contracts = Contract.objects.filter(counterparty=counterparty).order_by('-date')
    context = {
        "title": counterparty,
        "counterparty": counterparty,
        "contracts": contracts,

    }
    return render(request, "contracts/counterparty.html", context)


def download_contract_file(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    if not contract.file:
        raise Http404("Файл не найден")

    file_path = contract.file.path
    file_name = os.path.basename(file_path)  # Извлекается имя файла для заголовка Content-Disposition

    try:
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=file_name)
    except FileNotFoundError:
        raise Http404("Файл отсутствует на сервере")
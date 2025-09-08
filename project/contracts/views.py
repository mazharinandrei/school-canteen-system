import os

from django.contrib.auth.decorators import login_required
from django.http import Http404, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from project.views import ProjectBaseCreateView, ProjectBaseDetailView, ProjectBaseListView

from .forms import ContractForm, ContractFormSet, ContractFileUploadForm
from .models import Contract, Counterparty
from staff.models import get_staff_by_user



# Create your views here.
"""
LIST VIEWS
"""
class CounterpartyListView(ProjectBaseListView):
    model = Counterparty
    permission_required = "contracts.view_сounterparty"


class ContractListView(ProjectBaseListView):
    model = Contract
    permission_required = "contracts.view_contract"
    template_name = "contracts/all_contracts.html"


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


def render_contract(request, contract_id): #TODO: to CBV
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


class CounterpartyCreateView(ProjectBaseCreateView):
    model = Counterparty
    success_url = reverse_lazy("contracts:all_counterparties")


@login_required
def add_product_to_contract(request):
    return render(request, 'contracts/partials/add_product_to_contract_form.html',
                  {'formset': ContractFormSet()})

class CounterpartyDetailView(ProjectBaseDetailView):
    model = Counterparty
    template_name = "contracts/counterparty.html"


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
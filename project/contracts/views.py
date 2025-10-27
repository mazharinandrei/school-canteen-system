import os

from django.http import Http404, FileResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy

from project.views import (
    ParentChildrenCreateView,
    ProjectBaseCreateView,
    ProjectBaseDetailView,
    ProjectBaseListView,
)

from .forms import ContractCompositionForm, ContractForm, ContractFileUploadForm
from .models import Contract, ContractComposition, Counterparty


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

    def get_queryset(self):
        queryset = (
            Contract.objects.all()
            .select_related("counterparty")
            .select_related("staff")
            .prefetch_related("staff__position")
            .prefetch_related("products")
        )
        return queryset


def render_contract(request, contract_id):  # TODO: to CBV
    contract = Contract.objects.get(id=contract_id)

    if request.method == "POST" and not contract.file:
        form = ContractFileUploadForm(request.POST, request.FILES, instance=contract)
        if form.is_valid():
            form.save()
    else:
        form = ContractFileUploadForm(instance=contract)

    context = {
        "title": contract,
        "contract": contract,
        "form": form if not contract.file else None,
    }
    return render(request, "contracts/contract.html", context)


"""
CREATE VIEW
"""


class CounterpartyCreateView(ProjectBaseCreateView):
    model = Counterparty
    success_url = reverse_lazy("contracts:all_counterparties")


class ContractCreateView(ParentChildrenCreateView):
    parent_model = Contract
    child_model = ContractComposition

    parent_form_class = ContractForm
    child_form_class = ContractCompositionForm

    formset_kwargs = {"extra": 0, "min_num": 1, "validate_min": True}

    def get_success_url(self):
        return reverse_lazy("contracts:render_contract", args=[self.object.pk])


"""
DETAIL VIEW
"""


class CounterpartyDetailView(ProjectBaseDetailView):
    model = Counterparty
    template_name = "contracts/counterparty.html"


def download_contract_file(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    if not contract.file:
        raise Http404("Файл не найден")

    file_path = contract.file.path
    file_name = os.path.basename(
        file_path
    )  # Извлекается имя файла для заголовка Content-Disposition

    try:
        return FileResponse(
            open(file_path, "rb"), as_attachment=True, filename=file_name
        )
    except FileNotFoundError:
        raise Http404("Файл отсутствует на сервере")

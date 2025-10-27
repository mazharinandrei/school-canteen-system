from django.urls import path

from . import views


app_name = "contracts"

urlpatterns = [
    path("", views.ContractListView.as_view(), name="all_contracts"),
    path(
        "create_contract/", views.ContractCreateView.as_view(), name="create_contract"
    ),
    path(
        "contract/<int:contract_id>", views.render_contract, name="render_contract"
    ),  # TODO: to CBV
    path(
        "all_counterparties/",
        views.CounterpartyListView.as_view(),
        name="all_counterparties",
    ),
    path(
        "create_counterparty/",
        views.CounterpartyCreateView.as_view(),
        name="create_counterparty",
    ),
    path(
        "counterparty/<int:pk>",
        views.CounterpartyDetailView.as_view(),
        name="render_counterparty",
    ),
    path(
        "contracts/<int:pk>/download/",
        views.download_contract_file,
        name="download_contract_file",
    ),
]

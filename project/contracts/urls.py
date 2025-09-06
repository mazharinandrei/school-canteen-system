from django.conf import settings
from django.template.context_processors import static
from django.urls import path
from . import views


app_name = 'contracts'

urlpatterns = [
    path('all_contracts/', views.render_all_contracts, name='all_contracts'),
    path('create_contract/', views.create_contract, name='create_contract'),
    path("contract=<int:contract_id>", views.render_contract, name="render_contract"),
    path('all_counterparties/', views.render_counterparties, name='all_counterparties'),
    path('create_counterparty/', views.create_counterparty, name='create_counterparty'),
    path("counterparty=<int:counterparty_id>", views.render_counterparty, name="render_counterparty"),
    path('add-product-to-contract/', views.add_product_to_contract, name='add-product-to-contract'),
    path('contracts/<int:pk>/download/', views.download_contract_file, name='download_contract_file'),

]
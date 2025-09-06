from django.urls import path
from . import views


app_name = 'export'

urlpatterns = [
    path('dishes', views.export_dishes, name='dishes'),
    path("menu", views.export_menu, name="menu"),
    path("menu-requirement", views.export_menu_requirement, name="menu_requirement"),
    path("products-calc", views.export_products_calc, name="products_calc"),
    path("acceptance", views.export_acceptance, name="acceptance"),
    path("write-off", views.export_write_off, name="write_off"),
    path("availability", views.export_availability, name="availability"),
    path("costs-of-dishes", views.export_costs_of_dishes, name="costs_of_dishes"),
    path("tm/<int:tm_id>", views.export_technological_map, name="tm"),
]
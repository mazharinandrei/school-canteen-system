from django.urls import path

from . import views

app_name = "warehouse"

urlpatterns = [
    path("acceptance", views.AcceptanceListView.as_view(), name="acceptance"),
    path("acceptance/create", views.create_acceptance, name="create_acceptance"),
    path(
        "add-product-to-acceptance/",
        views.add_product_to_acceptance,
        name="add-product-to-acceptance",
    ),
    path("write_off", views.WriteOffListView.as_view(), name="write_off"),
    path("write_off/create", views.create_write_off, name="create_write_off"),
    path(
        "add-product-to-write_off/",
        views.add_product_to_write_off,
        name="add-product-to-write_off",
    ),
    path("availability", views.AvailabilityListView.as_view(), name="availability"),
    path(
        "load-products-for-acceptance",
        views.load_products_for_acceptance,
        name="load-products-for-acceptance",
    ),
    path(
        "render-acceptance-form",
        views.render_acceptance_form,
        name="render-acceptance-form",
    ),
    path("issue-menu", views.issue_menu, name="issue_menu"),
    path("transfers", views.ProductTransferListView.as_view(), name="transfers"),
    path("cook_menu", views.on_cook_menu_button_click, name="cook_menu"),
]

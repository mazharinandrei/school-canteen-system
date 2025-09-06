from django.urls import path
from . import views
from .forms import TechnologicalMapUpdateView

app_name = 'dishes'

urlpatterns = [
    path('all', views.render_dishes, name='all'),
    path('create', views.create_dish, name='create_dish'),

    path('categories', views.render_all_categories, name='all_food_categories'),
    path('create_category', views.create_category, name='create_category'),
    path('category=<int:category_id>', views.render_category, name='food_category'),

    path('technological_map/<pk>/edit/',
         TechnologicalMapUpdateView.as_view(), name='update_technological_map'),
    path('technological_map/<int:dish_id>/create', views.create_technological_map,
         name='create_technological_map'),
    path('technological_map/<technological_map_id>/', views.render_technological_map,
         name='technological_map_by_tm_id'),

    path('technological_map', views.render_technological_map, name='technological_map'),

    path('add-product-to-tm/', views.add_product_to_tm, name='add-product-to-tm'),
]
from django.urls import path
from . import views

app_name = 'dishes'

urlpatterns = [
    path('all', views.DishesByCategoryListView.as_view(), name='all'),
    path('dish/create', views.DishCreateView.as_view(), name='create_dish'),

    path('categories', views.FoodCategoryListView.as_view(), name='all_food_categories'),
    path('category/create', views.FoodCategoryCreateView.as_view(), name='create_category'),
    path('category/<int:pk>', views.FoodCategoryDetailView.as_view(), name='food_category'),

    path('technological_map/<int:dish_pk>/create', 
         views.create_technological_map,
         name='create_technological_map'),

     path('dish/<int:dish_pk>/technological_map', 
         views.redirect_to_tm, 
         name="technological_map_by_dish_id"), 

     path('technological_map/<int:pk>/', 
          views.TechnologicalMapDetailView.as_view(), 
          name='technological_map_by_tm_id-test'),

    path('add-product-to-tm/', views.add_product_to_tm, name='add-product-to-tm'),
]
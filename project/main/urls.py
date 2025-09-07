from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path('', views.index, name='home'),
    path('menu_requirement/', views.MenuRequirementListView.as_view(), name='menu_requirement'),  # TODO: меню и меню-требования это разные вещи
    path('menu/<str:date>/', views.render_menu, name='menu'), #TODO: detailview

    path('menu/today/', views.render_today_menu_requirement, name="today_menu_requirement"),

    path('products-calc', views.generate_schedule, name='products_calc'),

    path('cycle-menu', views.render_cycle_menu, name='cycle_menu'),

    path("create_menu_requirement", views.create_menu_requirement, name="create_menu_requirement"),
    path("add_dish_to_menu_requirement/<int:meal_type_id>", views.add_dish_to_menu_requirement,
         name="add_dish_to_menu_requirement"),

    path("cycle_menu_day/", views.render_cycle_menu_day),
    path("create-cycle-menu-day/<int:student_feeding_category>&<int:week_number>&<int:week_day>",
         views.create_cycle_menu_day, name="create-cycle-menu-day"),

    path("load_cycle_menu_composition_custom_form/<int:category>&<int:meal_type>",
         views.load_cycle_menu_composition_custom_form, name="load_cycle_menu_composition_custom_form"),

    path("create-application-for-student-meals",
         views.ApplicationCreateView.as_view(), name="create_application_for_student_meals"),
    
    path("applications/", views.ApplicationListView.as_view(), name="applications_for_student_meals"),
   
    path("delete-application-for-student-meals/<int:pk>",
         views.delete_application_for_student_meals, name="delete_application_for_student_meals"),
    
    path("render-edit-application-for-student-meals-modal-form/<int:pk>",
         views.render_application_for_student_meals_modal_form,
         name="edit_application_for_student_meals_modal_form"),
]
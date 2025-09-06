from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('all_staff/', views.render_all_staffs, name='all_staffs'),
    path('create_staff/', views.create_staff, name='create_staff'),
    path("staff/<int:staff_id>", views.render_staff, name="render_staff"),

    path('all_positions/', views.render_all_positions, name='all_positions'),
    path('position/<int:position_id>', views.render_position, name='render_position'),
    path('create_position/', views.create_position, name='create_position'),

    path("login/", views.LoginUser.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
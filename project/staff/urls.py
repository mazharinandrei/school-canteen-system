from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('all_staff/', views.StaffListView.as_view(), name='all_staffs'),
    path('create_staff/', views.StaffCreateView.as_view(), name='create_staff'),
    path("staff/<int:staff_id>", views.render_staff, name="render_staff"),

    path('all_positions/', views.PositionListView.as_view(), name='all_positions'),
    path('position/<int:pk>', views.PositionDetailView.as_view(), name='render_position'),
    path('create_position/', views.PositionCreateView.as_view(), name='create_position'),

    path("login/", views.LoginUser.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
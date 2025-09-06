from django.contrib import admin
from django.urls import path, include



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls', namespace="main")),
    path('warehouse/', include('warehouse.urls', namespace="warehouse")),
    path('dishes/', include('dishes.urls', namespace="dishes")),
    path('contracts/', include('contracts.urls', namespace="contracts")),
    path('staff/', include('staff.urls', namespace="staff")),
    path('reports/', include('reports.urls', namespace="reports")),
    path('export/', include('export.urls', namespace="export")),

]

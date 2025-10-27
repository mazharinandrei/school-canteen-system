from django.contrib.auth.decorators import permission_required
from django.contrib.auth.forms import AuthenticationForm

from django.shortcuts import render
from django.urls import reverse_lazy

from project.views import (
    ProjectBaseCreateView,
    ProjectBaseDetailView,
    ProjectBaseListView,
)

from .models import Staff, Positions
from contracts.models import Contract

from django.contrib.auth.views import LoginView

# Create your views here.

"""
LIST VIEWS 
"""


class StaffListView(ProjectBaseListView):
    model = Staff


class PositionListView(ProjectBaseListView):
    model = Positions


class StaffCreateView(
    ProjectBaseCreateView
):  # создание пользователя врядли должно так выглядеть
    model = Staff
    "staff.add_staff"
    fields = ("surname", "name", "second_name", "position", "note")


class PositionCreateView(ProjectBaseCreateView):
    "staff.add_position"

    model = Positions


@permission_required("staff.view_staff")
def render_staff(request, staff_id):
    staff = Staff.objects.get(id=staff_id)
    contracts = Contract.objects.filter(staff=staff)
    context = {
        "title": f"Информация о сотруднике {staff.surname_and_initials()}.",
        "staff": staff,
        "contracts": contracts,
    }
    return render(request, "staff.html", context)


@permission_required("staff.view_position")
def render_position(request, position_id):
    position = Positions.objects.get(id=position_id)
    staffs = Staff.objects.filter(position=position)
    context = {
        "title": f"Информация о должности {position.name}",
        "position": position,
        "staffs": staffs,
    }
    return render(request, "position.html", context)


class PositionDetailView(ProjectBaseDetailView):
    model = Positions

    def get_context_data(self, **kwargs):
        con = super().get_context_data(**kwargs)
        print(self.__dict__)
        return con


class LoginUser(LoginView):
    form_class = AuthenticationForm
    template_name = "base_form.html"
    extra_context = {"title": "Вход", "button_text": "Войти"}

    def get_success_url(self):
        return reverse_lazy("main:home")

from django.contrib.auth.forms import AuthenticationForm

from django.urls import reverse_lazy

from project.views import (
    ProjectBaseCreateView,
    ProjectBaseDetailView,
    ProjectBaseListView,
)

from .models import Staff, Positions
from contracts.models import Contract

from django.contrib.auth.views import LoginView


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
    model = Positions


class StaffDetailView(ProjectBaseDetailView):
    model = Staff
    template_name = "staff.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contracts"] = Contract.objects.filter(staff=self.object.pk)
        context["title"] = (
            f"Информация о сотруднике {self.object.surname_and_initials()}"
        )
        return context


class PositionDetailView(ProjectBaseDetailView):
    model = Positions


class LoginUser(LoginView):
    form_class = AuthenticationForm
    template_name = "base_form.html"
    extra_context = {"title": "Вход", "button_text": "Войти"}

    def get_success_url(self):
        return reverse_lazy("main:home")

from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect

from .forms import PositionForm, StaffForm, LoginUserForm
from .models import Staff, Positions
from contracts.models import Contract


# Create your views here.

@login_required
@permission_required('staff.view_staff')
def render_all_staffs(request):
    staffs = Staff.objects.all()
    context = {
        "title": "Все сотрудники",
        "staffs": staffs,

    }
    return render(request, "all_staffs.html", context)


@login_required
@permission_required('staff.add_staff')
def create_staff(request):
    form = StaffForm()
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            n = form.save()
            return redirect("/staff/all_staff/")
    else:
        context = {
            "title": "Добавить сотрудника",
            "form": form,
        }
    return render(request, "create_staff.html", context)

@permission_required('staff.view_staff')
def render_staff(request, staff_id):
    staff = Staff.objects.get(id=staff_id)
    contracts = Contract.objects.filter(staff=staff)
    context = {
        "title": f"Информация о сотруднике {staff.surname_and_initials()}.",
        "staff": staff,
        "contracts": contracts,

    }
    return render(request, "staff.html", context)

@permission_required('staff.view_position')
def render_position(request, position_id):
    position = Positions.objects.get(id=position_id)
    staffs = Staff.objects.filter(position=position)
    context = {
        "title": f"Информация о должности {position.name}",
        "position": position,
        "staffs": staffs,
    }
    return render(request, "position.html", context)

@permission_required('staff.view_position')
def render_all_positions(request):
    positions = Positions.objects.all()
    context = {
        "title": "Все должности",
        "positions": positions,
    }
    return render(request, "all_positions.html", context)

@permission_required('staff.add_position')
def create_position(request):
    form = PositionForm()

    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            n = form.save()
            return redirect("/staff/all_positions/")
    else:
        context = {
            "title": "Добавить должность",
            "form": form,
        }
        return render(request, "create_position.html", context)


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'login.html'
    extra_context = {'title': 'Авторизация'}

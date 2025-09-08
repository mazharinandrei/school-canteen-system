import datetime
from datetime import timedelta

from django.contrib.auth.decorators import permission_required, login_required
from django.forms import formset_factory

from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.utils.timezone import localdate

from project.views import ProjectBaseCreateView, ProjectBaseDetailView, ProjectBaseListView

from .forms import (OrderCalculationForm, MenuRequirementForm, \
                    menu_requirement_composition_formset, MenuRequirementCompositionForm,
                    CycleMenuCompositionCustomForm, CycleMenuCustomForm, ApplicationForStudentMealsForm)

from .models import MenuRequirement, MenuRequirementComposition, CycleMenu, CycleMenuComposition, MealType, \
    StudentFeedingCategory, ApplicationForStudentMeals

from dishes.models import Dish, FoodCategory

from .services.application_for_meals_info import (get_total_by_student_feeding_category)
from .services.menu_info import get_menu_product_composition, get_menu_nutrients, get_cycle_menu_day_composition
from dishes.services import get_dish_composition, get_cost_of_dish

from .services.products_calc import products_calc_by_date_interval, get_cycle_menu_by_date


# Create your views here.
@login_required
def index(request):
    return render(request, 'main/index.html')

class MenuRequirementListView(ProjectBaseListView):
    model = MenuRequirement
    template_name = "base_list.html"


def render_menu(request, date):
    menu_info = []
    cost_of_menu = 0
    no_cost = False
    try:
        menu_requirement = MenuRequirement.objects.get(date=date)
    except MenuRequirement.DoesNotExist:
        return render(request,
                      'main/menu_404.html',
                      {"date": date})

    for meal_type in MealType.objects.all():
        menu_composition = MenuRequirementComposition.objects.filter(meal_type=meal_type,
                                                                     menu_requirement=menu_requirement)
        meal_info = {
            "meal_type": meal_type,
            "dishes": []
        }

        for menu_composition_element in menu_composition:
            cost = get_cost_of_dish(menu_composition_element.dish,
                                    menu_composition_element.volume_per_student * menu_requirement.students_number)
            meal_info["dishes"].append({
                "dish": menu_composition_element.dish,
                "volume_per_student": menu_composition_element.volume_per_student,
                "cost": cost,
                "composition": get_dish_composition(menu_composition_element.dish,
                                                    menu_composition_element.volume_per_student)
            })
        menu_info.append(meal_info)

    nutrients, no_tm = get_menu_nutrients(menu_requirement)

    try:
        full_composition = get_menu_product_composition(menu_requirement)

    except Exception as e:
        full_composition = []

    for el in full_composition:
        try:
            cost_of_menu += el["cost"]
        except:
            no_cost = True

    context = {
        "title": f"Меню-требование на {date}",
        "menu_requirement": menu_requirement,
        "menu_info": menu_info,
        "full_composition": full_composition,
        "nutrients": nutrients,
        "no_tm": no_tm,
        "cost": cost_of_menu,
        "no_cost": no_cost
    }
    return render(request, 'main/menu.html', context)


@login_required
def render_today_menu_requirement(request):
    today = localdate()
    return render_menu(request, today)


@login_required
def generate_schedule(request):
    if request.method == 'POST':
        start_date = request.POST.get('first_date')
        end_date = request.POST.get('second_date')
        student_feeding_category = request.POST.get('student_feeding_category')
        planned_people_number = int(request.POST.get('planned_people_number'))

        products = products_calc_by_date_interval(start_date=start_date,
                                                  end_date=end_date,
                                                  student_feeding_category=student_feeding_category,
                                                  planned_people_number=planned_people_number)

        context = {
            "title": "Формирование заявки на продукты",
            "form": OrderCalculationForm(request.POST),
            "products": products,
            "start_date": start_date,
            "end_date": end_date,
            "student_feeding_category": student_feeding_category,
            "planned_people_number": planned_people_number,
        }

    else:
        form = OrderCalculationForm()
        context = {
            "title": "Формирование заявки на продукты",
            'form': form
        }

    return render(request, 'main/schedule_template.html', context)


@login_required
def render_cycle_menu(request): #TODO: очень неочевидные вещи в контексте
    student_feeding_categories = StudentFeedingCategory.objects.all()
    context = {
        "title": "Цикличное меню",
        "student_feeding_categories": student_feeding_categories,
    }
    return render(request, "main/cycle_menu.html", context)


@login_required
def render_cycle_menu_day(request):
    week_number = request.GET['week_input']
    student_feeding_category = request.GET['category_select']

    m = []

    week_days = CycleMenu.WeekDay.choices[:5]
    for week_day in week_days:
        m.append({
            "week_day": week_day,
            "composition": get_cycle_menu_day_composition(week_number=week_number,
                                                          week_day=week_day[0],
                                                          student_feeding_category=student_feeding_category)
        })
    context = {
        "m": m,
        "week_number": week_number,
        "student_feeding_category": student_feeding_category,

    }
    return render(request, "main/partials/cycle_menu_day.html", context)


def create_cycle_menu_day(request, student_feeding_category, week_number, week_day):
    if request.method == "POST":
        # TODO: перенести всё это в функцию с аргументом request.POST, student_feeding_category, week_number, week_day
        meal_types = request.POST.getlist('meal_type')
        volumes = request.POST.getlist('volume_per_student')
        dishes = request.POST.getlist('dish')
        actual_since = request.POST.get('actual_since')
        for i in range(len(dishes)):
            # TODO: сделать так, чтобы нельзя было изменять меню, созданное не в этом вызове функции

            cycle_menu, created = CycleMenu.objects.get_or_create(week_number=week_number,
                                                                  week_day=week_day,
                                                                  meal_type=MealType.objects.get(pk=meal_types[i]),
                                                                  student_feeding_category=StudentFeedingCategory.objects.get(
                                                                      pk=student_feeding_category),
                                                                  created_at=localdate(),
                                                                  actual_since=actual_since)
            CycleMenuComposition(cycle_menu_day=cycle_menu,
                                 volume_per_student=volumes[i],
                                 dish=Dish.objects.get(pk=dishes[i])).save()
        return redirect(reverse('main:cycle_menu'))
    context = {
        'week_number': week_number,
        'week_day': CycleMenu.WeekDay.choices[week_day - 1],
        'student_feeding_category': StudentFeedingCategory.objects.get(id=student_feeding_category),
        'title': "Добавление цикличного меню",
        'meal_types': MealType.objects.all(),
        'food_categories': FoodCategory.objects.all(),
        'cycle_menu_form': CycleMenuCustomForm(),
    }
    return render(request, "main/create_cycle_menu_day.html", context)


def load_cycle_menu_composition_custom_form(request, category, meal_type):
    form = CycleMenuCompositionCustomForm(category=category)
    form.initial = {"meal_type": meal_type}
    context = {
        "dishes": Dish.objects.filter(category=category),
        'form': form,
    }
    return render(request, "main/partials/load_cycle_menu_composition_custom_form.html", context)


@login_required
@permission_required('main.add_menurequirement')
def create_menu_requirement(request):
    m = []  # TODO: ублюдское название 1

    if request.method == 'POST':
        form = MenuRequirementForm(request.POST)
        form_meal_types = request.POST.getlist("form-0-meal_type")  # menurequirementcomposition_set
        dishes = request.POST.getlist("form-0-dish")
        volumes_per_students = request.POST.getlist("form-0-volume_per_student")

        data_for_formset = {
            "menurequirementcomposition_set-TOTAL_FORMS": str(len(form_meal_types)),
            "menurequirementcomposition_set-INITIAL_FORMS": "0",
        }

        for i in range(len(form_meal_types)):
            data_for_formset[f"menurequirementcomposition_set-{i}-meal_type"] = form_meal_types[
                i]  # menurequirementcomposition_set
            data_for_formset[f"menurequirementcomposition_set-{i}-dish"] = dishes[i]
            data_for_formset[f"menurequirementcomposition_set-{i}-volume_per_student"] = volumes_per_students[i]

        formset = menu_requirement_composition_formset(data_for_formset)

        if form.is_valid() and formset.is_valid():
            menu_reqierement = form.save()
            formset.instance = menu_reqierement
            formset.save()
            return redirect('/menu_requirement')

    else:
        student_feeding_category = ''
        students_number = ''

        if request.GET.get('student_feeding_category'):
            student_feeding_category = request.GET['student_feeding_category']

        if request.GET.get('students_number'):
            students_number = request.GET['students_number']

        new_formset = formset_factory(MenuRequirementCompositionForm, extra=0)
        meal_types = MealType.objects.all()

        id = 1  # TODO: какой к чёрту id
        for meal_type in meal_types:

            forms_for_meal_type = []

            if student_feeding_category and students_number:
                week_number, week_day = get_cycle_menu_by_date(localdate() + timedelta(days=1))
                try:
                    cycle_menu_day = CycleMenu.objects.filter(meal_type=meal_type,
                                                              student_feeding_category=student_feeding_category,
                                                              week_number=week_number,
                                                              week_day=week_day,
                                                              actual_since__lte=localdate()).latest('actual_since')

                    for el in CycleMenuComposition.objects.filter(cycle_menu_day=cycle_menu_day):
                        forms_for_meal_type.append(
                            new_formset(initial=[{"meal_type": meal_type,
                                                  "dish": el.dish,
                                                  "volume_per_student": el.volume_per_student}])[0]
                        )
                except:
                    pass

            d = {  # TODO: ублюдское название 2
                "id": id,
                "meal_type": meal_type,
                "formset": new_formset(initial=[{"meal_type": meal_type}])[0],  # abc
                "forms_for_meal_type": forms_for_meal_type
            }
            id += 1
            m.append(d)

        form = MenuRequirementForm(initial={'student_feeding_category': student_feeding_category,
                                            "students_number": students_number,
                                            "date": (localdate() + timedelta(days=1)).strftime("%Y-%m-%d"),
                                            })

    context = {
        "title": f"Сформировать меню-требование",
        'form': form,
        'm': m,
        # "formset21": formset21,
        # "new_formset": new_formset2,
    }
    return render(request, 'main/create_menu_requirement.html', context)


def add_dish_to_menu_requirement(request, meal_type_id):
    for abc in menu_requirement_composition_formset():
        abc.initial = {"meal_type": meal_type_id}
    context = {'el':
                   {'formset': abc}
               }
    return render(request, 'main/partials/add_dish_to_menu_requirement.html', context)


class ApplicationCreateView(ProjectBaseCreateView):
    model = ApplicationForStudentMeals
    form_class = ApplicationForStudentMealsForm
    fields = None
    success_url = reverse_lazy('main:applications_for_student_meals')


class ApplicationListView(ProjectBaseListView):
    model = ApplicationForStudentMeals
    template_name = "main/list_application_for_student_meals.html" # TODO: переделать
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_by_student_feeding_category'] = get_total_by_student_feeding_category()
        context['today'] = localdate() + timedelta(days=1), # TODO: если это завтра, почему это today?
        return context


def render_application_for_student_meals(request, application_id):
    application_for_student_meals = ApplicationForStudentMeals.objects.get(id=application_id)

    context = {
        "title": "Заявка на питание учеников",
        "application": application_for_student_meals,
    }
    return render(request, "main/application_for_student_meals.html", context)


def render_application_for_student_meals_modal_form(request, pk):
    application = ApplicationForStudentMeals.objects.get(id=pk)
    application.date = application.date.strftime("%Y-%m-%d")
    form = ApplicationForStudentMealsForm(instance=application)
    context = {
        "form": form,
    }
    return render(request,
                  "main/partials/application_for_student_meals_modal_form.html",
                  context)


@permission_required('main.delete_applicationforstudentmeals')
def delete_application_for_student_meals(request, pk):
    applications_for_student_meals_list = ApplicationForStudentMeals.objects.get(id=pk)

    if applications_for_student_meals_list.date <= localdate():
        pass
    else:
        applications_for_student_meals_list.delete()
    applications_for_student_meals_list = ApplicationForStudentMeals.objects.all().order_by('-date')
    context = {
        "applications": applications_for_student_meals_list,
    }
    return render(request, "main/partials/applications_for_student_meals_list.html", context)

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.timezone import localdate

from main.models import (
    NutrientNormative,
    list_actual_menus_for_feeding_category,
    count_actual_cycle_menu_days,
    StudentFeedingCategory,
)

from dishes.models import Dish, TechnologicalMap

from dishes.services import get_dish_composition

from reports.services.abc_analysis import (
    generate_abc_analysis_table,
    get_products_by_categories,
)


from contracts.services.services import get_product_cost


@login_required
def render_costs_of_dishes_report(request):
    dishes = Dish.objects.all()
    products_without_price = []
    dishes_with_no_tm = []
    for dish in dishes:
        dish.cost = 0

        try:
            dish.composition = get_dish_composition(dish)
        except TechnologicalMap.DoesNotExist:
            dishes_with_no_tm.append(dish)
            continue

        for el in dish.composition:
            if get_product_cost(el.product):
                el.cost = (
                    get_product_cost(el.product) / 1000 * float(el.volume_per_portion)
                )
            else:
                el.cost = 0

        for el in dish.composition:
            if el.cost:
                dish.cost += el.cost
            else:
                dish.cost = 0
                if el.product not in products_without_price:
                    products_without_price.append(el.product)
                break

    context = {
        "title": "Отчёт по стоимости блюд",
        "dishes": dishes,
        "products_without_price": products_without_price,
        "dishes_with_no_tm": dishes_with_no_tm,
    }
    return render(request, "reports/cost_of_dishes_report.html", context=context)


@login_required
def render_nutrients_normative_report_first_page(request):
    student_feeding_categories = StudentFeedingCategory.objects.all()
    context = {
        "title": "Отчёт по пищевой ценности рациона",
        "student_feeding_categories": student_feeding_categories,
    }
    return render(
        request, "reports/nutrients_normative_report_first_page.html", context=context
    )


@login_required
# Create your views here.
def render_nutrients_normative_report(request):
    student_feeding_category = request.GET["category_select"]
    try:
        normative = NutrientNormative.objects.filter(
            student_feeding_category=student_feeding_category,
            actual_since__lte=localdate(),
        ).latest("actual_since")
    except Exception:
        normative = NutrientNormative()
        normative.calories = 0
        normative.proteins = 0
        normative.fats = 0
        normative.carbohydrates = 0
        context = {
            "title": "Отчёт по пищевой ценности рациона",
            "student_feeding_category": student_feeding_category,
            "error": "Нет норматива",
            "normative": normative,
        }
        return render(
            request, "reports/partials/nutrients_normative_report.html", context=context
        )

    cyclic_menus = list_actual_menus_for_feeding_category(student_feeding_category)
    actual_cycle_menu_days_count = count_actual_cycle_menu_days(
        student_feeding_category
    )

    calories, proteins, fats, carbohydrates = 0, 0, 0, 0
    for menu in cyclic_menus:
        menu_calories, menu_proteins, menu_fats, menu_carbohydrates = (
            menu.get_nutrients()
        )
        calories += menu_calories
        proteins += menu_proteins
        fats += menu_fats
        carbohydrates += menu_carbohydrates

    normative.calories *= actual_cycle_menu_days_count
    normative.proteins *= actual_cycle_menu_days_count
    normative.fats *= actual_cycle_menu_days_count
    normative.carbohydrates *= actual_cycle_menu_days_count

    context = {
        "title": "Отчёт по пищевой ценности рациона",
        "student_feeding_category": student_feeding_category,
        "cyclic_menus": cyclic_menus,
        "normative": normative,
        "calories": calories,
        "proteins": proteins,
        "fats": fats,
        "carbohydrates": carbohydrates,
    }
    return render(request, "reports/partials/nutrients_normative_report.html", context)


@login_required
def render_abc_analysis_report(request):
    products_by_categories = get_products_by_categories()
    context = {
        "title": "Отчёт по ABC анализу",
        "table_url": reverse("reports:abc_analysis_table"),
        "products_by_categories": products_by_categories,
    }
    return render(request, "reports/abc_analysis_report.html", context)


@login_required
def render_abc_analysis_table(request):
    report_table = generate_abc_analysis_table()
    return HttpResponse(report_table)

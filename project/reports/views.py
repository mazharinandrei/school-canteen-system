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

from reports.services.abc_analysis import (
    generate_abc_analysis_table,
    get_products_by_categories,
)


from contracts.services.services import get_actual_product_costs


@login_required
def render_costs_of_dishes_report(request):
    dishes = (
        Dish.objects.all()
        .prefetch_related("technological_maps")
        .prefetch_related("technological_maps__composition")
        .prefetch_related("technological_maps__composition__product")
    )
    products_without_price = []
    dishes_with_no_tm = []

    product_costs = {
        product.name: product.avg_cost for product in get_actual_product_costs()
    }

    for dish in dishes:
        dish.cost = 0

        try:
            # TODO: решение нужно переработать
            dish.composition = list(dish.technological_maps.latest().composition.all())
        except TechnologicalMap.DoesNotExist:
            dishes_with_no_tm.append(dish)
            continue

        for el in dish.composition:
            if product_costs.get(el.product.name):
                el.cost = product_costs.get(el.product.name) / 1000 * el.volume
                dish.cost += el.cost
            else:
                el.cost = 0
                products_without_price.append(el.product)

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

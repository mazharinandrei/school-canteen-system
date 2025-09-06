from django.contrib.auth.decorators import permission_required, login_required
from django.http import FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from .forms import DishForm, TechnologicalMapForm, TechnologicalMapFormSet

from .models import FoodCategory, Dish, TechnologicalMap, TechnologicalMapComposition


# Create your views here.
@login_required
def render_dishes(request):
    context = {
        "title": "Все блюда",
        "data": {},
    }
    categories = FoodCategory.objects.all()
    for category in categories:
        context["data"][category] = Dish.objects.filter(category=category.id)
    return render(request, 'dishes/dishes.html', context)


@login_required
@permission_required('dishes.add_dish')
def create_dish(request):
    if request.method == 'POST':
        form = DishForm(request.POST)
        if form.is_valid():
            n = form.save()
            return redirect(f'technological_map/{n.id}/create')
        else:
            context = {
                "title": "Добавить блюдо",
                "form": form,
            }
            return render(request, 'dishes/dish_form.html', context)
    form = DishForm()
    context = {
        "title": "Добавить блюдо",
        "form": form,
    }
    return render(request, 'dishes/dish_form.html', context)


@login_required
def render_all_categories(request):
    food_categories = FoodCategory.objects.all()
    context = {
        "title": "Все категории",
        "food_categories": food_categories,
    }
    return render(request, "dishes/categories.html", context)


def render_category(request, category_id):
    category = FoodCategory.objects.get(id=category_id)
    dishes = Dish.objects.filter(category=category.id)
    context = {
        "title": f"Блюда категории \"{category.name}\"",
        "dishes": dishes,
    }
    return render(request, 'dishes/category.html', context)


@login_required
@permission_required('dishes.add_foodcategory')
def create_category(request):
    context = {
        "title": "Добавить категорию",
    }
    return render(request, "dishes/categories.html", context)


def render_technological_map(request, technological_map_id=False, technological_map_slug=False):
    technological_map = None
    tm_composition = None
    if technological_map_id:
        technological_map = TechnologicalMap.objects.get(id=technological_map_id)
        tm_composition = TechnologicalMapComposition.objects.filter(technological_map=technological_map_id)

    if technological_map_slug:  # TODO: добавить slug в модель
        technological_map = TechnologicalMap.objects.get(id=1)
        tm_composition = TechnologicalMapComposition.objects.filter(technological_map=1)

    try:
        if request.GET.get('dish'):
            dish_id = request.GET.get('dish')
            technological_map = Dish.objects.get(id=dish_id).get_actual_technological_map()
            tm_composition = TechnologicalMapComposition.objects.filter(technological_map=technological_map.id)
    except:
        pass

    context = {
        "title": technological_map,
        "technological_map": technological_map,
        'tm_composition': tm_composition,
    }

    if technological_map and tm_composition:
        return render(request, 'dishes/technological_map.html', context)
    else:
        return redirect(reverse_lazy('dishes:all'))


@permission_required('dishes.add_technologicalmap')
def create_technological_map(request, dish_id):
    dish = get_object_or_404(Dish, pk=dish_id)
    if request.method == 'POST':

        form = TechnologicalMapForm(request.POST)

        products = request.POST.getlist("product")
        volumes = request.POST.getlist("volume")

        data_for_formset = {
            "technologicalmapcomposition_set-TOTAL_FORMS": str(len(products)),
            "technologicalmapcomposition_set-INITIAL_FORMS": "0",
        }
        for i in range(len(products)):
            data_for_formset[f"technologicalmapcomposition_set-{i}-product"] = products[i]
            data_for_formset[f"technologicalmapcomposition_set-{i}-volume"] = volumes[i]

        formset = TechnologicalMapFormSet(data_for_formset)

        if form.is_valid() and formset.is_valid():
            technological_map = form.save(commit=False)
            technological_map.dish = dish
            technological_map.save()
            formset.instance = technological_map
            formset.save()
            return redirect('/dishes/all')
    else:
        form = TechnologicalMapForm()
        formset = TechnologicalMapFormSet()
    context = {
        "title": f"Добавить ТТК {dish}",
        'form': form,
        'formset': formset,
        'dish': dish,
    }
    return render(request, 'dishes/create_technological_map.html', context)


def add_product_to_tm(request):
    return render(request, 'dishes/partials/add_product_to_tc_form.html',
                  {'formset': TechnologicalMapFormSet()})


def export_dishes(request):
    result_path = generate_dishes_file(date=request.GET.get('date'),
                                       student_feeding_category=request.GET.get('student-feeding-category'))
    return FileResponse(open(result_path, 'rb'), as_attachment=True)

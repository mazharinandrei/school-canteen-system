from django.contrib.auth.decorators import permission_required, login_required
from django.http import FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy

from project.views import ProjectBaseCreateView, ProjectBaseDetailView, ProjectBaseListView

from .forms import TechnologicalMapForm, TechnologicalMapFormSet

from .models import FoodCategory, Dish, TechnologicalMap, TechnologicalMapComposition


"""
LIST VIEWS
"""


class FoodCategoryListView(ProjectBaseListView):
    model = FoodCategory
    template_name = "dishes/categories.html"

class DishesByCategoryListView(ProjectBaseListView):
    model = FoodCategory
    template_name = "dishes/dishes.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Блюда по категориям"
        return context

class DishCreateView(ProjectBaseCreateView):
    model = Dish
    
    def get_success_url(self):
        return reverse("dishes:create_technological_map", args=[self.object.pk])


class FoodCategoryDetailView(ProjectBaseDetailView):
    model = FoodCategory
    template_name = 'dishes/category.html'


class FoodCategoryCreateView(ProjectBaseCreateView):
    model = FoodCategory
    success_url = reverse_lazy("dishes:all_food_categories")

class TechnologicalMapDetailView(ProjectBaseDetailView):
    model = TechnologicalMap
    template_name = 'dishes/technological_map.html'


def redirect_to_tm(request, dish_pk):
    dish = get_object_or_404(Dish, pk=dish_pk)
    tm = dish.get_actual_technological_map()
    if dish_pk:
        return reverse_lazy("dishes:technological_map_by_tm_id", args=[tm.pk])


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

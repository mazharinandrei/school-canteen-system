from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy

from export.services.export_dishes import generate_dishes_file
from project.views import (
    ProjectBaseCreateView,
    ProjectBaseDetailView,
    ProjectBaseListView,
    ParentChildrenCreateView,
)

from .forms import (
    TechnologicalMapForm,
    TechnologicalMapCompositionForm,
)

from .models import FoodCategory, Dish, TechnologicalMap, TechnologicalMapComposition


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
    template_name = "dishes/category.html"


class FoodCategoryCreateView(ProjectBaseCreateView):
    model = FoodCategory
    success_url = reverse_lazy("dishes:all_food_categories")


class TechnologicalMapDetailView(ProjectBaseDetailView):
    model = TechnologicalMap
    template_name = "dishes/technological_map.html"


def redirect_to_tm(request, dish_pk):
    dish = get_object_or_404(Dish, pk=dish_pk)
    tm = dish.technological_maps.actual()
    if dish_pk:
        return reverse_lazy("dishes:technological_map_by_tm_id", args=[tm.pk])


class TechnologicalMapCreateView(ParentChildrenCreateView):
    dish = None
    object = None
    parent_model = TechnologicalMap
    child_model = TechnologicalMapComposition

    parent_form_class = TechnologicalMapForm
    child_form_class = TechnologicalMapCompositionForm
    formset_kwargs = {"extra": 0, "min_num": 1, "validate_min": True}
    template_name = "dishes/create_technological_map.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dish_pk = self.kwargs.get("dish_pk")
        self.dish = get_object_or_404(Dish, pk=dish_pk)

        context["dish_pk"] = dish_pk
        context["title"] = f"Добавить ТТК {self.dish}"

        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.get_context_data()
        self.object.dish = self.dish
        return super().form_valid(form)


def export_dishes(request):
    result_path = generate_dishes_file(
        date=request.GET.get("date"),
        student_feeding_category=request.GET.get("student-feeding-category"),
    )
    return FileResponse(open(result_path, "rb"), as_attachment=True)

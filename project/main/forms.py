from datetime import timedelta

from django import forms
from django.forms import DateInput, NumberInput, inlineformset_factory, Select
from django.utils.timezone import localdate

from .models import (
    MenuRequirement,
    MenuRequirementComposition,
    MealType,
    StudentFeedingCategory,
    ApplicationForStudentMeals,
)
from dishes.models import Dish, FoodCategory


class OrderCalculationForm(forms.Form):
    student_feeding_category = forms.ModelChoiceField(
        queryset=StudentFeedingCategory.objects.all(), label="Категория питающихся"
    )
    student_feeding_category.widget = forms.Select(
        attrs={
            "class": "form-select",
        }
    )

    first_date = forms.DateField(label="С")
    first_date.widget = forms.DateInput(
        attrs={
            "type": "date",
            "class": "form-control",
        }
    )

    second_date = forms.DateField(label="До")
    second_date.widget = forms.DateInput(
        attrs={
            "type": "date",
            "class": "form-control",
        }
    )

    planned_people_number = forms.IntegerField(
        label="Планируемое количество питающихся"
    )
    planned_people_number.widget = forms.NumberInput(
        attrs={
            "class": "form-control",
        }
    )


class MenuRequirementForm(forms.ModelForm):
    class Meta:
        model = MenuRequirement
        fields = ("date", "students_number", "student_feeding_category")

        widgets = {
            "date": DateInput(
                attrs={
                    "placeholder": "Дата меню-требования",
                    "type": "date",
                    "class": "form-control",
                }
            ),
            "students_number": NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Количество учеников",
                }
            ),
            "student_feeding_category": Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }


class MenuRequirementCompositionForm(forms.ModelForm):
    class Meta:
        model = MenuRequirementComposition
        fields = (
            "dish",
            "volume_per_student",
            "meal_type",
        )  # TODO: Хочу select2 в форме

        widgets = {
            "meal_type": NumberInput(attrs={"style": "display: none;"}),
            "volume_per_student": NumberInput(
                attrs={
                    "class": "form-control mb-3",
                    "placeholder": "Объём одной порции, гр.",
                }
            ),
            "dish": Select(
                attrs={
                    "class": "form-select mb-3",
                }
            ),
        }


menu_requirement_composition_formset = forms.inlineformset_factory(
    MenuRequirement,
    MenuRequirement.dishes.through,
    form=MenuRequirementCompositionForm,
    extra=1,
)
MenuRequirementCompositionFormSet = inlineformset_factory(
    MenuRequirement,
    MenuRequirementComposition,
    form=MenuRequirementCompositionForm,
    extra=1,
)


class CycleMenuCompositionCustomForm(forms.Form):
    dish = forms.ModelChoiceField(
        queryset=Dish.objects.none(),
        empty_label="выберите...",
        label="",
        widget=forms.Select(attrs={"class": "form-select mb-3"}),
    )

    meal_type = forms.ModelChoiceField(
        queryset=MealType.objects.all(), widget=forms.HiddenInput()
    )

    volume_per_student = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={
                "class": "form-control mb-3",
                "placeholder": "Объём одной порции, гр.",
            }
        )
    )

    def __init__(self, category, *args, **kwargs):
        super().__init__()
        self.fields["dish"].queryset = Dish.objects.filter(category=category).order_by(
            "name"
        )
        self.fields["dish"].label = FoodCategory.objects.get(id=category).name
        self.fields["dish"].name = f"dish_{category}"


class CycleMenuCustomForm(forms.Form):
    actual_since = forms.DateField(
        label="цикличное меню актуально с:",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )


class ApplicationForStudentMealsForm(forms.ModelForm):
    date = forms.DateField(
        initial=(localdate() + timedelta(days=1)).strftime("%Y-%m-%d"),
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="Дата заявки",
    )

    class Meta:
        model = ApplicationForStudentMeals
        fields = ("date", "grade", "students_number")
        widgets = {
            "grade": Select(attrs={"class": "form-control", "empty_label": "Класс"}),
            "students_number": NumberInput(
                attrs={"class": "form-control", "placeholder": "Количество учеников"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get("date") < localdate():
            self.add_error("date", "Дата не может быть меньше текущей")

        if ApplicationForStudentMeals.objects.filter(
            date=cleaned_data.get("date"), grade=cleaned_data.get("grade")
        ).exists():
            self.add_error(
                "date",
                f"Заявка для {cleaned_data.get('grade')} класса на данный день уже существует",
            )

        if (
            cleaned_data.get("students_number")
            > cleaned_data.get("grade").students_number
        ):
            self.add_error(
                "students_number",
                "Количество учеников не может быть больше количества учеников в классе",
            )

        return cleaned_data

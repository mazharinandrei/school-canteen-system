from django import forms
from django.forms import Textarea, DateInput, NumberInput, TextInput, Select
from django.views.generic import CreateView, UpdateView

from .models import TechnologicalMapComposition, Dish, TechnologicalMap, Product


class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ['name', 'category']  # TODO: category
        widgets = {
            'name': TextInput(attrs={
                'label': '',
                'placeholder': 'Название блюда',
                'class': 'form-control',
            }),
            'category': Select(attrs={
                'class': 'form-select',
                'label': 'Категория блюда',
            }),

        }

class TechnologicalMapUpdateView(UpdateView):  # TODO: не обновить ТК, а создать новую на основе старой мб
    model = TechnologicalMap
    fields = ["date", 'dish', 'calories', 'proteins', 'fats', 'carbohydrates', 'recipe', 'products']
    template_name_suffix = "_update_form"


class TechnologicalMapForm(forms.ModelForm):
    class Meta:
        model = TechnologicalMap
        fields = ('date', 'calories', 'proteins', 'fats', 'carbohydrates', 'recipe')
        # TODO: сделать ограничение на длину и значения (проверить модель)
        # TODO: дату меньше сегодняшней нельзя ввести (clean_date)
        widgets = {
            'date': DateInput(attrs={
                'placeholder': 'Дата смены',
                'type': 'date'
            }),

            'calories': NumberInput(attrs={
                "class": "form-control no-border",
            }),

            'proteins': NumberInput(attrs={
                "class": "form-control no-border",
            }),

            'fats': NumberInput(attrs={
                "class": "form-control no-border",
            }),

            'carbohydrates': NumberInput(attrs={

                "class": "form-control no-border",
            }),

            'recipe': Textarea(attrs={
                'class': "form-control mt-2",
                'placeholder': 'Введите технологию производства...'
            }),
        }


class TechnologicalMapCompositionForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), label="Продукт", empty_label="Продукт",
                                     widget=forms.Select(attrs={
                                         'class': 'form-select'
                                     }))
    volume = forms.DecimalField(label="Объём", max_digits=9, decimal_places=3, min_value=0.1,
                                widget=forms.TextInput(attrs={
                                    'class': 'form-control',
                                    'placeholder': 'Объем',
                                    "max": "99,999",

                                }))
    class Meta:
        model = TechnologicalMapComposition
        fields = ('product', 'volume')  # TODO: Хочу select2 в форме
        labels = {
            'product': 'Продукт',
            'volume': 'Объём'
        }


TechnologicalMapFormSet = forms.inlineformset_factory(TechnologicalMap, TechnologicalMap.products.through,
                                                      form=TechnologicalMapCompositionForm, extra=1)

from django import forms
from django.utils.timezone import localtime

from .models import Warehouse, Acceptance, WriteOffCause
from contracts.models import Contract
from dishes.models import Product

from .services.warehouse_transactions import (
    accept_to_warehouse,
    write_off_from_warehouse,
    is_volume_more_than_availability,
)


class AcceptanceForm(forms.ModelForm):
    warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.all(),
        empty_label="Выберите склад:",
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "placeholder": "Выберите склад",
            }
        ),
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.none(),
        empty_label="Выберите продукт:",
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "placeholder": "Выберите продукт",
            }
        ),
    )
    volume = forms.DecimalField(
        max_digits=9,
        decimal_places=3,
        min_value=0.1,
        label="Объем",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите объем",
                "maxlength": 9,
            }
        ),
    )
    contract = forms.ModelChoiceField(
        queryset=Contract.objects.all(),
        widget=forms.Select(
            attrs={
                "class": "form-select",
                "placeholder": "Выберите договор:",
            }
        ),
    )
    note = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": "Примечание"}
        ),
        required=False,
    )

    class Meta:
        model = Acceptance  # Связываем форму с моделью
        fields = ["warehouse", "product", "volume", "contract", "note"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "contract" in self.data:
            try:
                contract_id = int(self.data.get("contract"))
                self.fields["product"].queryset = Contract.objects.get(
                    id=contract_id
                ).products.all()
            except (ValueError, Contract.DoesNotExist):
                self.fields["product"].queryset = Product.objects.none()

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.datetime = localtime()
        accept_to_warehouse(
            instance.contract, instance.product, instance.volume, instance.warehouse
        )
        if commit:
            instance.save()
        return instance


class NewWriteOffForm(forms.Form):
    warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.all(),
        label="Склад",
        empty_label="Склад",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        label="Продукт",
        empty_label="Продукт",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    volume = forms.DecimalField(
        label="Объём",
        max_digits=9,
        decimal_places=3,
        min_value=0.1,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Объем",
                "max": "999999,999",
            }
        ),
    )

    cause = forms.ModelChoiceField(
        queryset=WriteOffCause.objects.all(),
        label="Причина списания",
        empty_label="Причина списания",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    note = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": "Примечание"}
        ),
        required=False,
    )

    def is_valid(self):
        valid = super(NewWriteOffForm, self).is_valid()
        print(self.cleaned_data)
        if is_volume_more_than_availability(
            self.cleaned_data["product"],
            self.cleaned_data["warehouse"],
            self.cleaned_data["volume"],
        ):
            valid = False
            self.add_error(
                "volume",
                f"На складе {self.cleaned_data['warehouse']} "
                f"меньше продукта \"{self.cleaned_data['product']}\", "
                f"чем планируется списать",
            )

        return valid

    def save(self):
        print(self.cleaned_data)
        data = self.cleaned_data
        try:
            write_off_from_warehouse(
                product=data["product"],
                volume=data["volume"],
                warehouse=data["warehouse"],
                cause=data["cause"],
                note=data["note"],
            )
        except Exception as e:
            print(e)
            self.add_error("product", e)

        return data

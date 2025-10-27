from django import forms
from django.forms import DateInput

from .models import Contract, ContractComposition


class ContractForm(forms.ModelForm):
    # staff = forms.ModelChoiceField(queryset=Staff.objects.all(), widget=forms.HiddenInput(), required=False)
    class Meta:
        model = Contract
        fields = ["date", "counterparty", "note"]
        widgets = {
            "date": DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "counterparty": forms.Select(attrs={"class": "form-select"}),
            "note": forms.TextInput(attrs={"placeholder": "..."}),
        }


class ContractCompositionForm(forms.ModelForm):
    class Meta:
        model = ContractComposition
        fields = ("product", "total_volume", "cost")
        widgets = {
            "product": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "total_volume": forms.NumberInput(
                attrs={"placeholder": "Количество по договору, кг"}
            ),
            "cost": forms.NumberInput(attrs={"placeholder": "Полная стоимость"}),
        }


ContractFormSet = forms.inlineformset_factory(
    Contract, Contract.products.through, form=ContractCompositionForm, extra=1
)


class ContractFileUploadForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ["file"]
        widgets = {
            "file": forms.FileInput(attrs={"class": "form-control", "id": "id_file"})
        }

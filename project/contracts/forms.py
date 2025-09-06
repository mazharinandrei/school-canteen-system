from django import forms
from django.forms import DateInput

from .models import Contract, Counterparty, ContractComposition
from staff.models import Staff


class CounterpartyForm(forms.ModelForm):
    class Meta:
        model = Counterparty
        fields = ("name", "address", "INN", "KPP")
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название',
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Адрес'
            }),
            'INN': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'ИНН'
            }),
            'KPP': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'КПП'
            }),
        }


class ContractForm(forms.ModelForm):
    #staff = forms.ModelChoiceField(queryset=Staff.objects.all(), widget=forms.HiddenInput(), required=False)
    class Meta:
        model = Contract
        fields = ['date', "counterparty", 'note']
        widgets = {
            'date': DateInput(attrs={
                'label': 'Дата договора',
                'type': 'date',
                'class': 'form-control'
            }),
            'counterparty': forms.Select(attrs={
                'class': 'form-select'
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Примечание'
            }),

        }
        labels = {
            'date': 'Дата договора',
            'counterparty': "Контрагент",
            'note': 'Примечание',
        }


class ContractCompositionForm(forms.ModelForm):
    class Meta:
        model = ContractComposition
        fields = ('product', 'total_volume', 'cost')
        labels = {
            'product': 'Продукт',
            'total_volume': 'Объём, кг',
            'cost': "Полная цена",
        }
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-select',
            }),
            'total_volume': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Объём, кг'

            }),
            'cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Полная цена'
            }),
        }


ContractFormSet = forms.inlineformset_factory(Contract,
                                              Contract.products.through,
                                              form=ContractCompositionForm,
                                              extra=1)

class ContractFileUploadForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                "id": "id_file"
            })
        }
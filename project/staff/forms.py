from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Staff, Positions


class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ("surname", "name", "second_name", "position")

        widgets = {
            'position': forms.Select(attrs={
                'class': 'form-select',
                'label': 'Должность'
            }),
            'surname': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Фамилия'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя'
            }),
            'second_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Отчество'
            }),
        }




class PositionForm(forms.ModelForm):
    class Meta:
        model = Positions
        fields = ['name']


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}))
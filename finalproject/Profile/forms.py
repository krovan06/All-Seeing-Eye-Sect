from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Request

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['title', 'body', 'file']
        widgets = {
            'title':forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'введие заголовок'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Введите текст заявки'}),
        }
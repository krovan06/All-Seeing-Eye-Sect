from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Request, UserProfile
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
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'введие заголовок'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Введите текст заявки'}),
        }

class ProfileEditForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label="Никнейм", required=True)
    email = forms.EmailField(label="Электронная почта", required=True)
    keep_avatar = forms.BooleanField(label="Оставить текущий аватар", required=False)

    class Meta:
        model = UserProfile
        fields = ['avatar', 'background']  # Поля для модели UserProfile

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user

        # Сохраняем никнейм и почту
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']

        # Если выбран чекбокс "Оставить текущий аватар", сбрасываем новое значение для аватара
        if self.cleaned_data.get('keep_avatar'):
            profile.avatar = self.instance.avatar

        if commit:
            user.save()
            profile.save()
        return profile
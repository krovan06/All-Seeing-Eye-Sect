from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Request, UserProfile, Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={  # Изменили TextInput на Textarea
                'placeholder': "коментарий..",
                'rows': 3,
                'class': 'comment-field',
                'id': 'commentText',
            }),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].error_messages.update({
            'unique': "Этот логин уже занят.",
        })
        self.fields['email'].error_messages.update({
            'invalid': "Введите корректный адрес",
            'required': "Ваша почта",
        })

    class Meta:
        model = User
        fields = ['username', 'email']

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['title', 'body', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'введие заголовок'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Введите текст заявки'}),
        }

class ProfileEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'user'):
            self.fields['username'].initial = self.instance.user.username


    username = forms.CharField(
        max_length=150,
        label="Никнейм",
        widget=forms.TextInput(attrs={
            'class': 'text-input',
            'placeholder': 'Введите новый никнейм...'
        }),
        required=True,
    )
    avatar = forms.ImageField(
        label="Сменить аватар:",
        widget=forms.FileInput(attrs={
            'class': 'file-input',
        }),
        required=False,
    )
    background = forms.ImageField(
        label="Сменить фон профиля:",
        widget=forms.FileInput(attrs={
            'class': 'file-input',
        }),
        required=False,
    )

    class Meta:
        model = UserProfile
        fields = ['avatar', 'background', 'username']

    def save(self, commit=True):
        print("ОП ОП сохраняем сохраняем")
        profile = super().save(commit=False)  # Получаем объект профиля без сохранения
        user = profile.user  # Доступ к связанному пользователю

        # Обновляем данные пользователя
        user.username = self.cleaned_data['username']

        if commit:
            user.save()  # Сохраняем изменения в модели User
            profile.save()  # Сохраняем профиль
        return profile
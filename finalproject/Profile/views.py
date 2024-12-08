from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UserForm
from django.contrib.auth.models import User
from .forms import UserRegistrationForm
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.views import View

@login_required
def redirect_to_profile(request):
    return redirect(f'/user/id/{request.user.id}/')
@login_required
def user_profile(request, id):
    user = get_object_or_404(User, id=id)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_profile', id=user.id)  # Перенаправляем на страницу профиля
    else:
        form = UserForm(instance=user)

    return render(request, 'Profile/user_profile.html', {'form': form, 'user': user})

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})

class CustomLoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'registration/login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(f'/user/id/{user.id}/')  # Перенаправляем в личный кабинет
        return render(request, 'registration/login.html', {'form': form})
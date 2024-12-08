from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UserForm  # Импортируйте форму, которую мы создадим позже
from django.contrib.auth.models import User

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

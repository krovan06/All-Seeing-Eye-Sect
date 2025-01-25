from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UserForm, UserRegistrationForm, RequestForm, ProfileEditForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from django.views import View
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import *
from django.http import HttpResponseForbidden
from django.db.models import Q
from rest_framework import generics
from .serializers import UserSerializer
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response

def request_list(request):
    # Получаем все заявки
    requests = Request.objects.all()  # Если модель заявок называется `Request`
    return render(request, 'requests/request_list.html', {'requests': requests})

def is_admin(user):
    return user.is_staff

@login_required
def view_request_detail(request, id):
    user_request = get_object_or_404(Request, id=id, user=request.user)
    return render(request, 'requests/request_detail.html', {'request': user_request})

@login_required
def my_requests(request):
    user_requests = Request.objects.filter(user = request.user).order_by('-created_at')
    return render(request, 'requests/my_requests.html', {'user_requests': user_requests})

@login_required
@staff_member_required
def manage_requests(request):
    query = request.GET.get('q', '')  # Получаем ключевые слова из параметра запроса
    if query:
        requests_list = Request.objects.filter(
            Q(title__icontains=query) | Q(body__icontains=query) | Q(user__username__icontains=query)
        )
    else:
        requests_list = Request.objects.all()
    return render(request, 'requests/manage_requests.html', {'requests_list': requests_list})

@login_required
def edit_request(request, id):
    # Проверяем, что заявка принадлежит текущему пользователю
    user_request = get_object_or_404(Request, id=id, user=request.user)

    if request.method == 'POST':
        form = RequestForm(request.POST, request.FILES, instance=user_request)
        if form.is_valid():
            # При редактировании заявки сбрасываем статус на "pending"
            edited_request = form.save(commit=False)
            edited_request.status = 'pending'  # Сбрасываем статус для повторного рассмотрения
            edited_request.save()
            messages.success(request, 'Заявка успешно обновлена и отправлена на повторное рассмотрение.')
            return redirect('my_requests')
    else:
        form = RequestForm(instance=user_request)

    return render(request, 'requests/edit_request.html', {'form': form, 'request_obj': user_request})

@login_required
@staff_member_required
def update_request_status(request, request_id, new_status):
    request_obj = get_object_or_404(Request, id=request_id)
    if new_status in ['approved', 'rejected', 'pending']:
        request_obj.status = new_status
        request_obj.save()
        messages.success(request, f"Статус заявки '{request_obj.title}' изменён на '{new_status}'.")
    else:
        messages.error(request, "Недопустимый статус.")
    return redirect('manage_requests')

@login_required
@user_passes_test(is_admin)
def delete_request(request, request_id):
    request_obj = get_object_or_404(Request, id=request_id)
    request_obj.delete()
    messages.success(request, f"Заявка '{request_obj.title}' успешно удалена.")
    return redirect('manage_requests')

def delete_request_by_user(request, request_id):
    """
    Удаление заявки обычным пользователем.
    """
    request_obj = get_object_or_404(Request, id=request_id)

    # Проверяем, что пользователь — автор заявки
    if request.user != request_obj.user:
        messages.error(request, "Вы можете удалять только свои заявки.")
        return redirect('my_requests')

    if request.method == 'POST':
        request_obj.delete()
        messages.success(request, "Заявка успешно удалена.")
        return redirect('my_requests')

    return render(request, 'requests/delete_confirm_user.html', {'request_obj': request_obj})

@staff_member_required
def approve_request(request, id):
    req = get_object_or_404(Request, id=id)
    req.status = 'approved'
    req.save()
    return redirect('manage_requests')

@staff_member_required
def reject_request(request, id):
    req = get_object_or_404(Request, id=id)
    req.status = 'rejected'
    req.save()
    return redirect('manage_requests')

@login_required
def create_request(request):
    if request.method == "POST":
        form = RequestForm(request.POST, request.FILES)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.user = request.user
            new_request.save()
            return redirect('my_requests')
    else:
        form = RequestForm()

    return render(request, 'requests/create_request.html', {'form': form})

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

def news_feed(request):
    # Получение только одобренных заявок
    approved_requests = Request.objects.filter(status='approved').order_by('-created_at')
    return render(request, 'news/news_feed.html', {'approved_requests': approved_requests})

#ПОЛЬЗОВАТЕЛИ
class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

# Получение, обновление и удаление конкретного пользователя

class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

@login_required
def redirect_to_profile(request):
    return redirect(f'/user/id/{request.user.id}/')

@login_required
def user_edit_profile(request, id):
    user = request.user

    # Убедимся, что у пользователя есть профиль
    if not hasattr(user, 'userprofile'):
        UserProfile.objects.create(user=user)

    profile = user.userprofile

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile, user=user)
        if form.is_valid():
            form.save()
            return redirect('user_profile', id=user.id)
    else:
        form = ProfileEditForm(instance=profile, user=user)

    return render(request, 'Profile/edit_profile.html', {'form': form})

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

    return render(request, 'Profile/user_lk.html', {'form': form, 'user': user})

class DeleteAccountView(LoginRequiredMixin, View):
    def post(self, request):
        user = request.user
        user.delete()  # Удаляет объект пользователя
        logout(request)  # Завершает сессию
        return redirect('login')


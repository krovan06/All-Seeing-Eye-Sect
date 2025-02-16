from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import *
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from django.views import View
from django.contrib.admin.views.decorators import staff_member_required
from .models import *
from django.db.models import Q
from rest_framework import generics
from .serializers import UserSerializer
from rest_framework.permissions import IsAdminUser
from django.shortcuts import render, redirect, get_object_or_404
from .models import RecoveryToken
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
import json



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
    approved_requests = Request.objects.filter(status='approved').order_by('-created_at')

    return render(request, 'news/news_feed.html', {
        'approved_requests': approved_requests,
    })


def post_detail(request, slug):
    post = get_object_or_404(Request, slug=slug)
    BANNED_WORDS = ["негр", "кровь", "fuck", "арбуз", "хуй"]

    def censor_text(comment):
        for word in BANNED_WORDS:
            comment = comment.replace(word, "&!%*!")  # Фильтр запрещенных слов
        return comment

    # Получаем все комментарии с вложенностью
    comments = Comment.objects.filter(post=post).select_related('user').prefetch_related('replies').order_by('created_at')
    comments = Comment.objects.filter(post=post).order_by('-created_at')
    form = CommentForm()

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        body = data.get("body")
        post_id = data.get("request_id")
        parent_id = data.get("parent_id", None)

        form = CommentForm({'body': body})

        if form.is_valid():
            try:
                req = Request.objects.get(id=post_id)
                comment = form.save(commit=False)
                comment.user = request.user
                comment.post = req
                comment.body = censor_text(comment.body)

                if parent_id:
                    parent_comment = Comment.objects.filter(id=parent_id).first()
                    if parent_comment:
                        comment.parent = parent_comment  # Привязываем к родительскому комментарию

                comment.save()

                return JsonResponse({
                    'success': True,
                    'username': comment.user.username if comment.user else "Аноним",
                    'body': comment.body,
                    'created_at': comment.created_at.strftime("%d.%m.%Y %H:%M"),
                    'parent_id': comment.parent.id if comment.parent else None
                })
            except Request.DoesNotExist:
                return JsonResponse({'success': False, 'error': "Пост не найден"}, status=400)

    return render(request, 'requests/post_detail.html', {
        'post': post,
        'form': form,
        'comments': comments
    })



def UserCommentsView (request):
    comments = Comment.objects.filter(user=request.user).select_related('post').order_by('-created_at')

    # Передаем комментарии в шаблон
    return render(request, 'comments/my_comments.html', {
        'comments': comments
    })


def home_page(request):
    return render(request, 'start-page/home.html')

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
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        print("опа пошли изменения")
        form = ProfileEditForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile', id=request.user.id)  # Редирект на профиль
    else:
        form = ProfileEditForm(instance=user_profile)

    return render(request, 'Profile/edit_profile.html', {'form': form, 'user': request.user})

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


def send_recovery_email(request):
    print("HOME")
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            print("LOCH")
            user = User.objects.get(email=email)
            print(user, "<-user")
            token, created = RecoveryToken.objects.get_or_create(user=user)
            print(token, "<-token")
            if not created:
                token.token = uuid.uuid4()
                token.save()

            # Формирование ссылки для восстановления
            reset_link = request.build_absolute_uri(
                reverse('recover_account', args=[token.token])
            )

            # Отправка email
            send_mail(
                'Восстановление аккаунта',
                f'Для восстановления аккаунта перейдите по ссылке: {reset_link}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            messages.success(request, 'Инструкции по восстановлению отправлены на ваш email.')
        except User.DoesNotExist:
            messages.error(request, 'Пользователь с таким email не найден.')

    return render(request, 'registration/password_reset_form.html')

def recover_account(request, token):
    try:
        recovery_token = RecoveryToken.objects.get(token=token)

        if not recovery_token.is_valid():
            messages.error(request, 'Срок действия токена истёк.')
            return redirect('send_recovery_email')

        # Восстановление: например, авторизация пользователя
        login(request, recovery_token.user)
        recovery_token.delete()  # Удаляем токен после использования
        messages.success(request, 'Аккаунт успешно восстановлен.')
        return redirect('user_profile', id=recovery_token.user.id)

    except RecoveryToken.DoesNotExist:
        messages.error(request, 'Неверный или недействительный токен.')
        return redirect('send_recovery_email')

#ПАРОЛИ
def password_reset(request):
    print("email улетел")
    user_email = request.user.email
    user = User.objects.get(email=user_email)
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    reset_link = request.build_absolute_uri(f'/password-reset-confirm/{uid}/{token}/')

    send_mail(
        'Сборс параля',
        f'Нажмите на ссылку для сброса вашего параля:{reset_link}',
        'krovan83@mail.ru',
        [user_email],
    )
    return render(request, 'registration/password_reset.html')


def password_reset_confirm(request, uidb64, token):
    try:
        # Раскодирование UID
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Проверка токена
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            # Получение нового пароля
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if new_password and new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Ваш пароль успешно изменён.')

                # Логин пользователя после смены пароля
                login(request, user)
                return redirect('login')
            else:
                messages.error(request, 'Пароли не совпадают или пусты.')

        # Рендер формы для смены пароля
        return render(request, 'recovery/send_email.html', {
            'validlink': True,
        })
    else:
        # Недействительная ссылка
        return render(request, 'recovery/send_email.html', {
            'validlink': False,
        })
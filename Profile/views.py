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
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views.generic import TemplateView
from .models import AccountRecoveryToken
from django.db.models import Case, When, Value, TextField, F
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
    user_requests = Request.objects.filter(user=request.user).order_by('-created_at')
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

@login_required
def clear_notifications(request):
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"success": False, "error": "Request is not AJAX"}, status=400)

    if request.method == 'POST':
        updated_count = Request.objects.filter(user=request.user, has_new_comments=True).update(has_new_comments=False)
        return JsonResponse({"success": True, "updated": updated_count})

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

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

            form.save()  # Сохраняем пользователя
            return JsonResponse({'success': True})  # Успешная регистрация
        else:
            # Если форма невалидна, возвращаем ошибки
            print(form.errors)
            return JsonResponse({'errors': form.errors}, status=400)

    form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def check_unique(request):
    field = request.GET.get('field')
    value = request.GET.get('value')

    if not field or not value:
        return JsonResponse({'error': 'Некорректные параметры'}, status=400)

    # Проверка уникальности для username
    if field == 'username' and User.objects.filter(username=value).exists():
        return JsonResponse({'unique': False})
    # Проверка уникальности для email
    if field == 'email' and User.objects.filter(email=value).exists():
        return JsonResponse({'unique': False})

    return JsonResponse({'unique': True})

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
    # comments = Comment.objects.filter(post=post, is_deleted=False).order_by('-created_at')
    comments = Comment.objects.filter(
        post=post
    ).annotate(
        display_body=Case(
            When(is_deleted=True, deleted_by=Comment.DELETED_BY_SYSTEM, then=Value("Пользователь удалил аккаунт")),
            default=F('body'),
            output_field=TextField(),
        )
    ).order_by('-created_at')
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

                        # Отправляем уведомление родительскому комментарию
                        # Например, добавляем поле has_replies для индикатора
                        # Например, добавляем поле has_replies для индикатора
                        parent_comment.has_replies = True
                        parent_comment.save()

                req.has_new_comments = True
                req.save(update_fields=["has_new_comments"])

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
        'comments': comments,
        'now': timezone.now()
,
    })

def mark_comment_read(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            comment_id = data.get("comment_id")
            comment = Comment.objects.get(id=comment_id)
            comment.has_replies = False  # Или другой флаг, обозначающий "прочитано"
            comment.save()
            return JsonResponse({"success": True})
        except Comment.DoesNotExist:
            return JsonResponse({"error": "Комментарий не найден"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Неверный JSON"}, status=400)
    return JsonResponse({"error": "Метод не поддерживается"}, status=405)


def edit_comment(request, comment_id):
    if request.method == "POST":
        try:
            comment = Comment.objects.get(id=comment_id, user=request.user)
            editing_started = json.loads(request.body).get("editing_started", False)

            # Проверяем, истекло ли время редактирования
            if timezone.now() > comment.editable_until and not editing_started:
                return JsonResponse({"error": "Время редактирования истекло"}, status=403)

            data = json.loads(request.body)
            new_body = data.get("body")

            if not new_body or new_body.strip() == "":
                return JsonResponse({"error": "Текст комментария не может быть пустым"}, status=400)

            comment.body = new_body.strip()
            comment.save()
            return JsonResponse({"success": True, "new_body": comment.body})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Некорректный JSON"}, status=400)
        except Comment.DoesNotExist:
            return JsonResponse({"error": "Комментарий не найден"}, status=404)

    return JsonResponse({"error": "Неверный метод"}, status=405)


def UserCommentsView(request):
    user_comments = Comment.objects.filter(user=request.user, is_deleted=False).order_by('-created_at')

    return render(request, 'comments/my_comments.html', {
        'comments': user_comments
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

    # Проверяем, есть ли новые комментарии в его заявках
    has_new_comments = Request.objects.filter(user=user, has_new_comments=True).exists()

    notifications = user.notifications.filter(is_read=False)  # Только непрочитанные уведомления

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_profile', id=user.id)
    else:
        form = UserForm(instance=user)

    return render(request, 'Profile/user_lk.html', {
        'form': form,
        'user': user,
        'notifications': notifications,
        'has_new_comments': has_new_comments  # Передаём в шаблон
    })

@login_required
def mark_notifications_as_read(request):
    request.user.notifications.update(is_read=True)
    return redirect('user_profile', id=request.user.id)

def is_valid_email(email):
    """Проверяет, является ли email валидным."""
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False
class DeleteAccountView(LoginRequiredMixin, View):
    def post(self, request):
        user_profile = request.user.userprofile
        user_profile.mark_deleted()

        # Создаём токен восстановления
        recovery_token, _ = AccountRecoveryToken.objects.get_or_create(
            user=request.user,
            defaults={"token": uuid.uuid4()}
        )

        # Отправляем письмо
        if is_valid_email(request.user.email):
            send_mail(
                'Восстановление аккаунта',
                f'Твой аккаунт можно восстановить в течение 30 дней. Перейди по ссылке: {request.build_absolute_uri(reverse("recover_account", args=[recovery_token.token]))}',
                settings.EMAIL_HOST_USER,
                [request.user.email],
                fail_silently=True,
            )

        logout(request)
        return redirect('delete_account')
class RestoreAccountView(View):
    def get(self, request, token):
        recovery_token = get_object_or_404(AccountRecoveryToken, token=token, is_used=False)

        if recovery_token.is_expired():
            messages.error(request, "Токен истёк. Восстановление невозможно.")
            return redirect('login')

        user = recovery_token.user
        user.is_active = True
        user.username = f"restored_user_{user.id}"  # Можешь сохранять старое имя, если хранишь его где-то
        user.save(update_fields=['is_active', 'username'])

        if hasattr(user, 'userprofile'):
            user_profile = user.userprofile
            user_profile.restore_account()

        recovery_token.is_used = True
        recovery_token.save()

        login(request, user)
        messages.success(request, "Ваш аккаунт успешно восстановлен.")

        return redirect('user_profile', id=user.id)

def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)  # Только владелец удаляет свой коммент

    if comment.replies.exists():  # Если есть ответы, заменяем текст и откладываем удаление
        comment.body = "Этот комментарий был удалён пользователем"
        comment.is_deleted = True
        comment.delete_time = now() + timedelta(minutes=15)  # Полное удаление через 15 минут
        comment.save()
    else:
        comment.delete()  # Если нет ответов, сразу удаляем

    messages.success(request, "Комментарий удалён")
    return redirect(request.META.get("HTTP_REFERER", "news_feed"))  # Возвращаем на страницу


def login_with_token(request, token):
    login_token = get_object_or_404(LoginToken, token=token)

    if not login_token.is_valid():
        messages.error(request, "Ссылка устарела, запросите новую.")
        return redirect('login')  # На страницу ввода email

    user = login_token.user
    login(request, user)

    # После успешного входа, удаляем токен
    login_token.delete()

    return redirect('user_profile', id=user.id)

def send_recovery_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)

            if hasattr(user, 'userprofile') and user.userprofile.is_deleted:
                # Аккаунт удалён — отправляем ссылку на восстановление
                AccountRecoveryToken.objects.filter(user=user).delete()
                token = AccountRecoveryToken.objects.create(user=user, token=uuid.uuid4())

                reset_link = request.build_absolute_uri(reverse('recover_account', args=[token.token]))

                send_mail(
                    'Восстановление аккаунта',
                    f'Для восстановления аккаунта перейдите по ссылке: {reset_link}',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                messages.success(request, 'Ссылка для восстановления аккаунта отправлена на ваш email.')

            else:
                # Аккаунт активен — создаём временный токен для входа
                login_token = LoginToken.generate_for(user)
                login_link = request.build_absolute_uri(reverse('login_with_token', args=[login_token]))

                send_mail(
                    'Ваш личный кабинет',
                    f'Для входа в ваш аккаунт перейдите по ссылке: {login_link}',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                messages.success(request, 'Ссылка для быстрого входа отправлена на ваш email.')

        except User.DoesNotExist:
            messages.error(request, 'Пользователь с таким email не найден.')

        return redirect('restore_or_exit')

class RestoreOrExitView(TemplateView):
    template_name = 'recovery/restore_or_exit.html'

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
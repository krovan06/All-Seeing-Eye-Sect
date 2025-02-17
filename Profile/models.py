from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F
import secrets
import uuid
from datetime import timedelta
from django.utils import timezone
from django.utils.timezone import now
from django.utils.text import slugify



class Request(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобренно'),
        ('rejected', 'Отклонено'),
    ]

    has_new_comments = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    body = models.TextField(verbose_name="Основной текс")
    file = models.FileField(
        upload_to='requests/files/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])],
        verbose_name='Изображение'
    )
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True, verbose_name='Slug')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            while Request.objects.filter(slug=self.slug).exists():
                self.slug = f"{self.slug}-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}"

class Comment(models.Model):
    post = models.ForeignKey(
        Request,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comments'
    )
    body = models.TextField()
    original_body = models.TextField(null=True, blank=True)  # Новое поле
    created_at = models.DateTimeField(auto_now_add=True)
    editable_until = models.DateTimeField(default=now() + timedelta(seconds=900))
    has_replies = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    delete_time = models.DateTimeField(null=True, blank=True)

    DELETED_BY_USER = 'user'
    DELETED_BY_SYSTEM = 'system'
    DELETED_BY_CHOICES = [
        (DELETED_BY_USER, 'User'),
        (DELETED_BY_SYSTEM, 'System'),
    ]
    deleted_by = models.CharField(
        max_length=10,
        choices=DELETED_BY_CHOICES,
        null=True,
        blank=True
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies"
    )

    def delete_comment(self):
        self.is_deleted = True
        self.delete_time = timezone.now() + timezone.timedelta(seconds=30)  # Через 5 минут
        self.deleted_by = Comment.DELETED_BY_USER
        self.save(update_fields=["is_deleted", "delete_time", "deleted_by"])

    def soft_delete(self):
        """Меняет текст комментария при удалении аккаунта"""
        if not self.is_deleted:
            self.original_body = self.body  # Сохраняем оригинальный текст
            self.body = "Пользователь удалил аккаунт"
            self.is_deleted = True
            self.save(update_fields=["body", "original_body", "is_deleted"])

    def restore(self):
        """Восстанавливает комментарий, если аккаунт возвращён"""
        if self.is_deleted and self.original_body:
            self.body = self.original_body  # Восстанавливаем оригинальный текст
            self.is_deleted = False
            self.save(update_fields=["body", "is_deleted"])

    def should_be_removed(self):
        """ Проверяет, нужно ли удалить комментарий окончательно """
        return self.is_deleted and self.delete_time and now() >= self.delete_time


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='userprofile'
    )
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    background = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    delete_time = models.DateTimeField(null=True, blank=True)  # Дата окончательного удаления
    is_deleted = models.BooleanField(default=False)  # Флаг удаления

    def mark_deleted(self):
        """Помечает аккаунт удалённым и обновляет комментарии"""
        self.is_deleted = True
        self.delete_time = timezone.now() + timedelta(days=30)
        self.user.is_active = False
        self.user.save()

        # # Помечаем комментарии как удалённые
        # Comment.objects.filter(user=self.user, is_deleted=False).update(
        #     original_body=F('body'),
        #     body="Пользователь удалил аккаунт",
        #     is_deleted=True,
        #     deleted_by=Comment.DELETED_BY_SYSTEM
        # )
        for comment in Comment.objects.filter(user=self.user, is_deleted=False):
            comment.soft_delete()
            comment.deleted_by = Comment.DELETED_BY_SYSTEM
            comment.save(update_fields=["body", "original_body", "is_deleted", "deleted_by"])

        self.save()

    def restore_account(self):
        """Восстанавливает аккаунт и комментарии"""
        self.is_deleted = False
        self.delete_time = None
        self.user.is_active = True
        self.user.save()

        # Восстанавливаем только комментарии, удалённые системой
        Comment.objects.filter(
            user=self.user,
            is_deleted=True,
            deleted_by=Comment.DELETED_BY_SYSTEM
        ).update(
            body=F('original_body'),
            is_deleted=False,
            deleted_by=None
        )

        self.save()

    def should_be_removed(self):
        """ Проверяет, истёк ли срок восстановления """
        return self.is_deleted and self.delete_time and timezone.now() >= self.delete_time

    def __str__(self):
        return self.user.username

class AccountRecoveryToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField(null=False, blank=False)

    def save(self, *args, **kwargs):
        if not self.expiration_date:
            self.expiration_date = now() + timedelta(days=1)  # Даем 24 часа на восстановление
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Токен для {self.user.username}"

    def is_expired(self):
        """Проверяет, истёк ли токен"""
        return timezone.now() > self.expiration_date


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class RecoveryToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return now() < self.created_at + timedelta(hours=24)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}"


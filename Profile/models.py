from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
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
        on_delete=models.SET_NULL,  # Изменяем CASCADE на SET_NULL
        null=True,                  # Разрешаем NULL
        blank=True,
        related_name='comments'
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    editable_until = models.DateTimeField(default=now() + timedelta(seconds=10))
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies"
    )

    def __str__(self):
        return f"Комментарий {self.user} к {self.post}"

class AccountRecoveryToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    @classmethod
    def generate_token(cls, user):
        token = secrets.token_urlsafe(48)
        return cls.objects.create(user=user, token=token)

    @property
    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(hours=24)

class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='userprofile')
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True)  # Путь к папке для аватаров
    background = models.ImageField(
        upload_to='backgrounds/',
        blank=True,
        null=True)  # Путь к папке для фона

    def __str__(self):
        return self.user.username


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


from celery import shared_task
from django.utils.timezone import now
from .models import Comment

@shared_task
def clear_deleted_comments():
    """Удаляет комментарии, которые были удалены пользователем более 5 минут назад"""
    comments_to_delete = Comment.objects.filter(
        is_deleted=True,
        deleted_by=Comment.DELETED_BY_USER,
        delete_time__lte=now()
    )
    count = comments_to_delete.count()
    comments_to_delete.delete()
    return count
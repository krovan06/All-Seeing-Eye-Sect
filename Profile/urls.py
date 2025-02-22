from django.urls import path, include
from .views import *
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('', home_page, name='home_page'),  # Стартовый URL
    path('register/', register, name='register'),
    path('user/id/<int:id>/', user_profile, name='user_profile'),
    path('login/', CustomLoginView.as_view(), name='login'),

    path('login-with-token/<str:token>/', login_with_token, name='login_with_token'),
    path('user/id/<int:id>/edit/', user_edit_profile, name='user_edit_profile'),

    path('check-unique/', check_unique, name='check-unique'),
    path('password-reset/', password_reset, name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),

    path('delete-account/', DeleteAccountView.as_view(), name='delete_account'),
    path('recover/', send_recovery_email, name='send_recovery_email'),

    path('restore-or-exit/', RestoreOrExitView.as_view(), name='restore_or_exit'),
    path('recover-account/<str:token>/', RestoreAccountView.as_view(), name='recover_account'),
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserRetrieveUpdateDestroyView.as_view(), name='user-detail'),

    path('requests/', request_list, name='request_list'),
    path('requests/create/', create_request, name='create_request'),
    path('requests/manage/', manage_requests, name='manage_requests'),
    path('requests/approve/<int:id>/', approve_request, name='approve_request'),
    path('requests/reject/<int:id>/', reject_request, name='reject_request'),
    path('requests/<int:request_id>/status/<str:new_status>/', update_request_status, name='update_request_status'),
    path('requests/<int:request_id>/delete/', delete_request, name='delete_request'),
    path('requests/my/', my_requests, name='my_requests'),
    path('requests/<int:id>/', view_request_detail, name='view_request_detail'),
    path('requests/<int:id>/edit/', edit_request, name='edit_request'),
    path('requests/<int:request_id>/user-delete/', delete_request_by_user, name='delete_request_by_user'),
    path('request/<slug:slug>/', views.post_detail, name='post_detail'),

    path('my-comments/', UserCommentsView, name='user_comments'),
    path('edit_comment/<int:comment_id>/', edit_comment, name='edit_comment'),
    path('delete-comment/<int:comment_id>/', delete_comment, name='delete_comment'),

    path("mark-comment-read/", mark_comment_read, name="mark_comment_read"),
    path('notifications/read/', mark_notifications_as_read, name='mark_notifications_as_read'),
    path('notifications/clear/', clear_notifications, name='clear_notifications'),

    path('news/', news_feed, name='news_feed'),
    path('home/', home_page, name='home_page'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

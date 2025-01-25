from django.urls import path, include
from .views import *
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('user/id/<int:id>/', user_profile, name='user_profile'),

    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('user/id/<int:id>/edit/', user_edit_profile, name='user_edit_profile'),

    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('delete-account/', views.DeleteAccountView.as_view(), name='delete_account'),
    path('recovery/', send_recovery_email, name='send_recovery_email'),
    path('recovery/<uuid:token>/', recover_account, name='recover_account'),

    path('', redirect_to_profile, name='redirect_to_profile'),
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

    path('news/', news_feed, name='news_feed'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
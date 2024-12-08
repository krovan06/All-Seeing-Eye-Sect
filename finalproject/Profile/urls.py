from django.urls import path, include
from .views import user_profile

urlpatterns = [
    path('user/id/<int:id>/', user_profile, name='user_profile'),
]

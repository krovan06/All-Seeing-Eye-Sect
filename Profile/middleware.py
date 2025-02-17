from django.shortcuts import redirect
from django.utils.timezone import now

class BlockDeletedUsersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            profile = getattr(request.user, 'userprofile', None)
            if profile and profile.is_deleted:
                return redirect('login')  # Перенаправляем на страницу входа

        return self.get_response(request)
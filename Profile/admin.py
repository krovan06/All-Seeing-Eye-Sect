from django.contrib import admin
from .models import Request

class RequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'created_at')  # Поля, которые будут отображаться в списке
    list_filter = ('status',)  # Фильтр по статусу
    search_fields = ('title', 'content', 'user__username')  # Поиск по полям
    actions = ['approve_requests', 'reject_requests']  # Действия

    def approve_requests(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, "Выбранные заявки одобрены.")

    def reject_requests(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, "Выбранные заявки отклонены.")

    approve_requests.short_description = "Одобрить выбранные заявки"
    reject_requests.short_description = "Отклонить выбранные заявки"

admin.site.register(Request, RequestAdmin)

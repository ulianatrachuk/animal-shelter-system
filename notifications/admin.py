from django.contrib import admin
from .models import Notification, AdminAlert


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "volunteer",
        "title",
        "is_read",
        "created_at",
    )
    list_filter = ("is_read", "created_at")
    search_fields = (
        "volunteer__first_name",
        "volunteer__last_name",
        "title",
        "message",
    )
    readonly_fields = ("created_at",)


@admin.register(AdminAlert)
class AdminAlertAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "volunteer",
        "title",
        "is_resolved",
        "created_at",
    )
    list_filter = ("is_resolved", "created_at")
    search_fields = (
        "volunteer__first_name",
        "volunteer__last_name",
        "title",
        "message",
    )
    readonly_fields = ("created_at",)
from django.contrib import admin
from .models import ChatRoom, ChatMessage


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 1
    fields = ("text", "is_from_admin", "created_at")
    readonly_fields = ("created_at",)


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ("id", "volunteer", "created_at")
    search_fields = (
        "volunteer__first_name",
        "volunteer__last_name",
        "volunteer__phone",
    )
    inlines = [ChatMessageInline]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "text", "is_from_admin", "created_at")
    list_filter = ("is_from_admin", "created_at")
    search_fields = ("text", "room__volunteer__first_name", "room__volunteer__last_name")
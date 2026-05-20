from django.contrib import admin
from django.utils.html import format_html
from .models import Animal
from walks.models import Walk


class WalkInline(admin.TabularInline):
    model = Walk
    extra = 0
    fields = (
        "planned_date",
        "planned_start_time",
        "planned_end_time",
        "status",
        "volunteer",
    )
    readonly_fields = fields
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('name', 'breed', 'age', 'sex', 'is_available', 'photo_preview')
    search_fields = ('name', 'breed')
    list_filter = ('sex', 'is_available')
    readonly_fields = ('photo_preview',)
    inlines = [WalkInline]

    fields = (
    'name',
    'breed',
    'age',
    'sex',
    'photo',
    'photo_preview',
    'health_status',
    'short_description',
    'is_available',
)

    @admin.display(description='Фото')
    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="90" height="90" style="object-fit: cover; border-radius: 12px;" />',
                obj.photo.url
            )
        return 'Немає фото'
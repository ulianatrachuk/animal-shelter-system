from django.contrib import admin
from django.utils.html import format_html
from .models import VolunteerProfile, VolunteerPreference, PreferenceCriterion


@admin.register(PreferenceCriterion)
class PreferenceCriterionAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


class VolunteerPreferenceInline(admin.TabularInline):
    model = VolunteerPreference
    extra = 0
    autocomplete_fields = ("criterion",)


@admin.register(VolunteerProfile)
class VolunteerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "phone",
        "display_walks_count",
        "missed_walks_count",
        "is_blocked",
        "photo_preview",
    )

    list_filter = (
        "is_blocked",
        "missed_walks_count",
    )

    search_fields = ("first_name", "last_name", "phone")

    readonly_fields = (
        "photo_preview",
        "missed_walks_count",
        "blocked_at",
        "block_reason",
    )

    inlines = [VolunteerPreferenceInline]

    fields = (
        "user",
        "first_name",
        "last_name",
        "phone",
        "birth_date",
        "profile_photo",
        "photo_preview",
        "missed_walks_count",
        "is_blocked",
        "blocked_at",
        "block_reason",
    )

    @admin.display(description="Walks count")
    def display_walks_count(self, obj):
        return obj.get_completed_walks_count()

    @admin.display(description="Фото")
    def photo_preview(self, obj):
        if obj.profile_photo:
            return format_html(
                '<img src="{}" width="90" height="90" style="object-fit: cover; border-radius: 12px;" />',
                obj.profile_photo.url,
            )
        return "Немає фото"


@admin.register(VolunteerPreference)
class VolunteerPreferenceAdmin(admin.ModelAdmin):
    list_display = ("id", "volunteer", "criterion", "is_enabled")
    list_filter = ("is_enabled", "criterion")
    search_fields = (
        "criterion__name",
        "volunteer__first_name",
        "volunteer__last_name",
    )
    autocomplete_fields = ("volunteer", "criterion")
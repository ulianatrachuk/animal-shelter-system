from django.contrib import admin
from .models import Walk
from reviews.models import BehaviorReview, AnimalSpecificTraitReview


class BehaviorReviewInline(admin.TabularInline):
    model = BehaviorReview
    extra = 0
    fields = ("trait", "score", "volunteer")
    readonly_fields = ("trait", "score", "volunteer")
    can_delete = False


class AnimalSpecificTraitReviewInline(admin.TabularInline):
    model = AnimalSpecificTraitReview
    extra = 0
    fields = ("trait", "answer", "volunteer")
    readonly_fields = ("trait", "answer", "volunteer")
    can_delete = False


@admin.register(Walk)
class WalkAdmin(admin.ModelAdmin):
    list_display = ("id", "animal", "volunteer", "planned_date", "status")
    list_filter = ("status", "planned_date", "animal")
    search_fields = (
        "animal__name",
        "volunteer__first_name",
        "volunteer__last_name",
    )
    inlines = [BehaviorReviewInline, AnimalSpecificTraitReviewInline]
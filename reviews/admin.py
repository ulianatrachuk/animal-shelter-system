from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import render
from django.db.models import Count, Avg, Q
from django.utils.html import format_html
from .services import analyze_comments_for_animal

from .models import BehaviorTrait, BehaviorReview, BehaviorComment, AnimalSpecificTrait, AnimalTraitSuggestion, AnimalSpecificTraitReview


@admin.register(BehaviorTrait)
class BehaviorTraitAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(BehaviorReview)
class BehaviorReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "animal", "trait", "score", "volunteer", "walk")
    list_filter = ("animal", "trait", "score")
    search_fields = (
        "animal__name",
        "trait__name",
        "volunteer__first_name",
        "volunteer__last_name",
    )

    change_list_template = "admin/reviews/behavior_review_changelist.html"

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "analytics/",
                self.admin_site.admin_view(self.analytics_animals_view),
                name="behavior_reviews_analytics",
            ),
            path(
                "analytics/animal/<int:animal_id>/",
                self.admin_site.admin_view(self.analytics_animal_detail_view),
                name="behavior_reviews_animal_detail",
            ),
            path(
                "analytics/animal/<int:animal_id>/trait/<int:trait_id>/",
                self.admin_site.admin_view(self.analytics_trait_detail_view),
                name="behavior_reviews_trait_detail",
            ),
            path(
                "analytics/animal/<int:animal_id>/specific-trait/<int:trait_id>/",
                self.admin_site.admin_view(self.analytics_specific_trait_detail_view),
                name="behavior_reviews_specific_trait_detail",
            ),
        ]

        return custom_urls + urls

    def analytics_animals_view(self, request):
        animals = (
            BehaviorReview.objects
            .values("animal_id", "animal__name")
            .annotate(
                reviews_count=Count("id"),
                traits_count=Count("trait", distinct=True),
            )
            .order_by("animal__name")
        )

        context = {
            **self.admin_site.each_context(request),
            "title": "Аналітика рис тварин",
            "animals": animals,
        }

        return render(
            request,
            "admin/reviews/behavior_animals_analytics.html",
            context,
        )

    def analytics_animal_detail_view(self, request, animal_id):
        animal_name = (
            BehaviorReview.objects
            .filter(animal_id=animal_id)
            .values_list("animal__name", flat=True)
            .first()
        )

        traits = (
            BehaviorReview.objects
            .filter(animal_id=animal_id)
            .values("trait_id", "trait__name")
            .annotate(
                reviews_count=Count("id"),
                avg_score=Avg("score"),
            )
            .order_by("trait__name")
        )
        specific_traits = (
            AnimalSpecificTraitReview.objects
            .filter(animal_id=animal_id)
            .values("trait_id", "trait__name")
            .annotate(
                yes_count=Count("id", filter=Q(answer=True)),
                no_count=Count("id", filter=Q(answer=False)),
                total_count=Count("id"),
            )
            .order_by("trait__name")
        )

        comments = (
            BehaviorComment.objects
            .filter(animal_id=animal_id)
            .select_related("volunteer", "walk")
            .order_by("-created_at")
        )

        context = {
            **self.admin_site.each_context(request),
            "title": f"Риси тварини: {animal_name}",
            "animal_id": animal_id,
            "animal_name": animal_name,
            "traits": traits,
            "specific_traits": specific_traits,
            "comments": comments,
        }

        return render(
            request,
            "admin/reviews/behavior_animal_detail.html",
            context,
        )

    def analytics_trait_detail_view(self, request, animal_id, trait_id):
        reviews = (
            BehaviorReview.objects
            .filter(animal_id=animal_id, trait_id=trait_id)
            .select_related("animal", "trait", "volunteer", "walk")
            .order_by("-created_at")
        )

        first_review = reviews.first()

        context = {
            **self.admin_site.each_context(request),
            "title": "Оцінки конкретної риси",
            "animal_id": animal_id,
            "trait_id": trait_id,
            "animal_name": first_review.animal.name if first_review else "—",
            "trait_name": first_review.trait.name if first_review else "—",
            "reviews": reviews,
        }

        return render(
            request,
            "admin/reviews/behavior_trait_detail.html",
            context,
        )
    
    def analytics_specific_trait_detail_view(self, request, animal_id, trait_id):
        reviews = (
            AnimalSpecificTraitReview.objects
            .filter(animal_id=animal_id, trait_id=trait_id)
            .select_related("animal", "trait", "volunteer", "walk")
            .order_by("-created_at")
        )

        first_review = reviews.first()

        context = {
            **self.admin_site.each_context(request),
            "title": "Відповіді по індивідуальній рисі",
            "animal_id": animal_id,
            "trait_id": trait_id,
            "animal_name": first_review.animal.name if first_review else "—",
            "trait_name": first_review.trait.name if first_review else "—",
            "reviews": reviews,
        }

        return render(
            request,
            "admin/reviews/behavior_specific_trait_detail.html",
            context,
        )


@admin.register(BehaviorComment)
class BehaviorCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "animal", "volunteer", "walk", "created_at")
    list_filter = ("animal", "created_at")
    search_fields = (
        "animal__name",
        "volunteer__first_name",
        "volunteer__last_name",
        "comment",
    )
    readonly_fields = ("created_at",)
    actions = ["run_ai_analysis_for_comments"]

    def run_ai_analysis_for_comments(self, request, queryset):
        animal_ids = queryset.values_list("animal_id", flat=True).distinct()

        from animals.models import Animal

        for animal in Animal.objects.filter(id__in=animal_ids):
            analyze_comments_for_animal(animal)

        self.message_user(request, "AI аналіз коментарів виконано")

    run_ai_analysis_for_comments.short_description = (
        "Запустити AI аналіз вибраних коментарів"
    )

@admin.register(AnimalSpecificTrait)
class AnimalSpecificTraitAdmin(admin.ModelAdmin):
    list_display = ("id", "animal", "name", "created_at")
    list_filter = ("animal",)
    search_fields = ("animal__name", "name")


@admin.register(AnimalTraitSuggestion)
class AnimalTraitSuggestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "animal",
        "suggested_trait_name",
        "comments_count",
        "is_approved",
        "is_rejected",
        "created_at",
    )
    list_filter = ("animal", "is_approved", "is_rejected")
    search_fields = ("animal__name", "suggested_trait_name", "summary")
    readonly_fields = ("summary", "comments_count", "created_at")
    actions = ["run_ai_analysis", "approve_suggestions", "reject_suggestions"]
    actions_on_top = True
    actions_on_bottom = True

    def run_ai_analysis(self, request, queryset):
        print("ADMIN ACTION STARTED")

        for suggestion in queryset:
            analyze_comments_for_animal(suggestion.animal)

        self.message_user(request, "AI аналіз виконано")

    def approve_suggestions(self, request, queryset):
        for suggestion in queryset:
            if suggestion.is_approved:
                continue

            # створюємо реальний критерій
            AnimalSpecificTrait.objects.get_or_create(
                animal=suggestion.animal,
                name=suggestion.suggested_trait_name
            )

            suggestion.is_approved = True
            suggestion.is_rejected = False
            suggestion.save()

        self.message_user(request, "Критерії успішно підтверджені")


    approve_suggestions.short_description = "Підтвердити та створити критерій"

    def reject_suggestions(self, request, queryset):
        queryset.update(is_rejected=True, is_approved=False)
        self.message_user(request, "Пропозиції відхилено")


    reject_suggestions.short_description = "Відхилити пропозиції"

@admin.register(AnimalSpecificTraitReview)
class AnimalSpecificTraitReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "animal", "trait", "answer", "volunteer", "walk", "created_at")
    list_filter = ("animal", "trait", "answer")
    search_fields = (
        "animal__name",
        "trait__name",
        "volunteer__first_name",
        "volunteer__last_name",
    )
    readonly_fields = ("created_at",)
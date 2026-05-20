from django.db import models
from django.db.models import Avg


class Animal(models.Model):
    SEX_CHOICES = [
        ("male", "Чоловіча"),
        ("female", "Жіноча"),
    ]

    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100, blank=True)
    age = models.PositiveIntegerField()
    sex = models.CharField(max_length=10, choices=SEX_CHOICES)

    photo = models.ImageField(
        upload_to="animals/photos/",
        null=True,
        blank=True
    )

    health_status = models.CharField(max_length=255, blank=True)
    short_description = models.TextField(blank=True)
    favorite_treats = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)

    qr_code = models.ImageField(
        upload_to="animals/qr/",
        null=True,
        blank=True
    )

    ai_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def rating_to_percent(self, avg_score):
        if avg_score is None:
            return 0

        return round(((avg_score - 1) / 4) * 100)

    def get_behavior_stats(self):
        from reviews.models import BehaviorReview

        stats = {}

        reviews = BehaviorReview.objects.filter(animal=self)

        traits = set(reviews.values_list("trait__name", flat=True))

        for trait in traits:
            avg_score = reviews.filter(trait__name=trait).aggregate(
                Avg("score")
            )["score__avg"]

            if avg_score is not None:
                percent = self.rating_to_percent(avg_score)
                stats[trait] = percent

        return stats
    def get_specific_trait_stats(self):
        from reviews.models import AnimalSpecificTraitReview

        stats = []

        traits = self.specific_traits.all()

        for trait in traits:
            reviews = AnimalSpecificTraitReview.objects.filter(
                animal=self,
                trait=trait
            )

            total = reviews.count()
            yes_count = reviews.filter(answer=True).count()
            no_count = reviews.filter(answer=False).count()

            yes_percent = round((yes_count / total) * 100) if total > 0 else 0

            stats.append({
                "id": trait.id,
                "name": trait.name,
                "yes_count": yes_count,
                "no_count": no_count,
                "total": total,
                "yes_percent": yes_percent,
            })

        return stats
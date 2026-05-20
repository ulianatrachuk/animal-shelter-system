from django.db import models
from animals.models import Animal
from walks.models import Walk
from users.models import VolunteerProfile


class BehaviorTrait(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class BehaviorReview(models.Model):
    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name="behavior_reviews"
    )
    walk = models.ForeignKey(
        Walk,
        on_delete=models.CASCADE,
        related_name="behavior_reviews"
    )
    volunteer = models.ForeignKey(
        VolunteerProfile,
        on_delete=models.CASCADE,
        related_name="behavior_reviews"
    )
    trait = models.ForeignKey(
        BehaviorTrait,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    score = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("walk", "trait")

    def __str__(self):
        return f"{self.animal.name} - {self.trait.name} - {self.score}"
    
class BehaviorComment(models.Model):
    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name="behavior_comments"
    )
    walk = models.ForeignKey(
        Walk,
        on_delete=models.CASCADE,
        related_name="behavior_comments"
    )
    volunteer = models.ForeignKey(
        VolunteerProfile,
        on_delete=models.CASCADE,
        related_name="behavior_comments"
    )

    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("walk", "volunteer")

    def __str__(self):
        return f"{self.animal.name} - {self.volunteer.get_full_name()}"
    
class AnimalSpecificTrait(models.Model):
    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name="specific_traits"
    )
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("animal", "name")

    def __str__(self):
        return f"{self.animal.name} - {self.name}"


class AnimalTraitSuggestion(models.Model):
    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name="trait_suggestions"
    )
    suggested_trait_name = models.CharField(max_length=255)
    summary = models.TextField()
    comments_count = models.PositiveIntegerField(default=0)

    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.animal.name} - {self.suggested_trait_name}"
    
class AnimalSpecificTraitReview(models.Model):
    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name="specific_trait_reviews"
    )
    walk = models.ForeignKey(
        Walk,
        on_delete=models.CASCADE,
        related_name="specific_trait_reviews"
    )
    volunteer = models.ForeignKey(
        VolunteerProfile,
        on_delete=models.CASCADE,
        related_name="specific_trait_reviews"
    )
    trait = models.ForeignKey(
        AnimalSpecificTrait,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    answer = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("walk", "volunteer", "trait")
        verbose_name = "Animal specific trait review"
        verbose_name_plural = "Animal specific trait reviews"

    def __str__(self):
        value = "Так" if self.answer else "Ні"
        return f"{self.animal.name} - {self.trait.name} - {value}"
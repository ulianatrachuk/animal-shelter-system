from django.conf import settings
from django.db import models
from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver


class VolunteerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="volunteer_profile"
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    birth_date = models.DateField(null=True, blank=True)

    profile_photo = models.ImageField(
        upload_to="volunteers/photos/",
        null=True,
        blank=True
    )

    missed_walks_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Кількість пропущених прогулянок"
    )

    is_blocked = models.BooleanField(
        default=False,
        verbose_name="Профіль заблоковано"
    )

    blocked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата блокування"
    )

    block_reason = models.TextField(
        blank=True,
        default="",
        verbose_name="Причина блокування"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_completed_walks_count(self):
        from walks.models import Walk

        return Walk.objects.filter(
            volunteer=self,
            status="completed",
            ended_at__isnull=False
        ).count()

    def get_favorite_completed_dog(self):
        from walks.models import Walk

        favorite = (
            Walk.objects.filter(
                volunteer=self,
                status="completed",
                ended_at__isnull=False
            )
            .values("animal__name")
            .annotate(total=Count("id"))
            .order_by("-total")
            .first()
        )

        if favorite:
            return favorite["animal__name"]

        return "Немає даних"


class PreferenceCriterion(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Preference criterion"
        verbose_name_plural = "Preference criteria"

    def __str__(self):
        return self.name


class VolunteerPreference(models.Model):
    volunteer = models.ForeignKey(
        VolunteerProfile,
        on_delete=models.CASCADE,
        related_name="preferences"
    )

    criterion = models.ForeignKey(
        PreferenceCriterion,
        on_delete=models.CASCADE,
        related_name="volunteer_preferences"
    )

    is_enabled = models.BooleanField(default=False)

    class Meta:
        unique_together = ("volunteer", "criterion")
        verbose_name = "Volunteer preference"
        verbose_name_plural = "Volunteer preferences"

    def __str__(self):
        return f"{self.volunteer.get_full_name()} - {self.criterion.name}"


@receiver(post_save, sender=VolunteerProfile)
def create_preferences_for_new_volunteer(sender, instance, created, **kwargs):
    if created:
        for criterion in PreferenceCriterion.objects.all():
            VolunteerPreference.objects.get_or_create(
                volunteer=instance,
                criterion=criterion,
                defaults={"is_enabled": False}
            )


@receiver(post_save, sender=PreferenceCriterion)
def add_new_criterion_to_all_volunteers(sender, instance, created, **kwargs):
    if created:
        for volunteer in VolunteerProfile.objects.all():
            VolunteerPreference.objects.get_or_create(
                volunteer=volunteer,
                criterion=instance,
                defaults={"is_enabled": False}
            )
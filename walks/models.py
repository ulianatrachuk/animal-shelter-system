from datetime import datetime, timedelta, time

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from users.models import VolunteerProfile
from animals.models import Animal


class Walk(models.Model):
    STATUS_CHOICES = [
        ("planned", "Запланована"),
        ("active", "Активна"),
        ("completed", "Завершена"),
        ("missed", "Пропущена"),
    ]

    volunteer = models.ForeignKey(
        VolunteerProfile,
        on_delete=models.CASCADE,
        related_name="walks"
    )
    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name="walks"
    )

    planned_date = models.DateField()
    planned_start_time = models.TimeField()
    planned_end_time = models.TimeField(null=True, blank=True)

    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="planned"
    )

    final_activity_score = models.PositiveSmallIntegerField(null=True, blank=True)
    unexpected_situations_comment = models.TextField(blank=True)
    character_match_comment = models.TextField(blank=True)
    overall_impression = models.PositiveSmallIntegerField(null=True, blank=True)
    completion_photo = models.ImageField(
        upload_to="walk_completion_photos/",
        null=True,
        blank=True
    )
    reminder_sent = models.BooleanField(default=False)
    half_hour_reminder_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.animal.name} - {self.volunteer.first_name} {self.volunteer.last_name} - {self.status}"

    def get_duration_seconds(self):
        if not self.started_at:
            return 0

        end_time = self.ended_at if self.ended_at else timezone.now()
        duration = end_time - self.started_at
        return int(duration.total_seconds())

    def get_duration_display(self):
        total_seconds = self.get_duration_seconds()

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def get_planned_duration_minutes(self):
        if not self.planned_start_time or not self.planned_end_time:
            return None

        start_dt = datetime.combine(self.planned_date, self.planned_start_time)
        end_dt = datetime.combine(self.planned_date, self.planned_end_time)

        return int((end_dt - start_dt).total_seconds() // 60)

    def clean(self):
        if self.planned_date < timezone.localdate():
            raise ValidationError("Не можна планувати прогулянку на минулу дату.")

        if self.planned_start_time < time(10, 0) or self.planned_start_time > time(17, 0):
            raise ValidationError("Початок прогулянки має бути в межах 10:00–17:00.")

        if self.planned_end_time:
            if self.planned_end_time > time(17, 0):
                raise ValidationError("Кінець прогулянки не може бути пізніше 17:00.")

            duration_minutes = self.get_planned_duration_minutes()

            if duration_minutes not in [30, 40]:
                raise ValidationError("Тривалість прогулянки має бути 30 або 40 хвилин.")

            if self.planned_end_time <= self.planned_start_time:
                raise ValidationError("Час завершення має бути пізніше часу початку.")

        existing_walk = Walk.objects.filter(
            animal=self.animal,
            planned_date=self.planned_date,
        ).exclude(pk=self.pk)

        if existing_walk.exists():
            raise ValidationError("Цей песик уже має прогулянку на вибрану дату.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
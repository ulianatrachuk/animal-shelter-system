from datetime import datetime, timedelta, time

from django.utils import timezone
from rest_framework import serializers

from .models import Walk


class WalkSerializer(serializers.ModelSerializer):
    animal_name = serializers.CharField(source="animal.name", read_only=True)
    volunteer_first_name = serializers.CharField(source="volunteer.first_name", read_only=True)
    volunteer_last_name = serializers.CharField(source="volunteer.last_name", read_only=True)
    duration_seconds = serializers.SerializerMethodField()
    duration_display = serializers.SerializerMethodField()
    is_over_one_hour = serializers.SerializerMethodField()
    needs_safety_check = serializers.SerializerMethodField()
    animal_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Walk
        fields = [
            "id",
            "animal",
            "animal_name",
            "animal_photo_url",
            "volunteer",
            "volunteer_first_name",
            "volunteer_last_name",
            "planned_date",
            "planned_start_time",
            "planned_end_time",
            "started_at",
            "ended_at",
            "status",
            "final_activity_score",
            "unexpected_situations_comment",
            "character_match_comment",
            "overall_impression",
            "duration_seconds",
            "duration_display",
            "is_over_one_hour",
            "needs_safety_check",
            "created_at",
            "completion_photo",
        ]

    def get_duration_seconds(self, obj):
        return obj.get_duration_seconds()

    def get_duration_display(self, obj):
        return obj.get_duration_display()

    def get_is_over_one_hour(self, obj):
        return obj.get_duration_seconds() > 3600

    def get_needs_safety_check(self, obj):
        return obj.status == "active" and obj.get_duration_seconds() > 3600

    def get_animal_photo_url(self, obj):
        request = self.context.get("request")

        if obj.animal and obj.animal.photo:
            if request:
                return request.build_absolute_uri(obj.animal.photo.url)
            return obj.animal.photo.url

        return None


class WalkCreateSerializer(serializers.ModelSerializer):
    duration_minutes = serializers.IntegerField(write_only=True)

    class Meta:
        model = Walk
        fields = [
            "animal",
            "planned_date",
            "planned_start_time",
            "duration_minutes",
        ]

    def validate_planned_date(self, value):
        if value < timezone.localdate():
            raise serializers.ValidationError("Не можна планувати прогулянку на минулу дату.")
        return value

    def validate_planned_start_time(self, value):
        if value < time(10, 0) or value > time(16, 30):
            raise serializers.ValidationError(
                "Початок прогулянки має бути в межах 10:00–16:30."
            )
        return value

    def validate_duration_minutes(self, value):
        if value not in [30, 40]:
            raise serializers.ValidationError("Тривалість прогулянки має бути 30 або 40 хв.")
        return value

    def validate(self, attrs):
        animal = attrs["animal"]
        planned_date = attrs["planned_date"]
        planned_start_time = attrs["planned_start_time"]
        duration_minutes = attrs["duration_minutes"]

        start_dt = datetime.combine(planned_date, planned_start_time)
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        planned_end_time = end_dt.time()

        if planned_end_time > time(17, 0):
            raise serializers.ValidationError(
                {"planned_start_time": "Прогулянка має завершитися не пізніше 17:00."}
            )

        existing_walk = Walk.objects.filter(
            animal=animal,
            planned_date=planned_date,
        )

        if existing_walk.exists():
            raise serializers.ValidationError(
                {"animal": "Цей песик уже має прогулянку на цю дату."}
            )

        attrs["planned_end_time"] = planned_end_time
        return attrs

    def create(self, validated_data):
        validated_data.pop("duration_minutes")
        planned_end_time = validated_data.pop("planned_end_time")

        volunteer = self.context["volunteer"]

        walk = Walk.objects.create(
            volunteer=volunteer,
            planned_end_time=planned_end_time,
            status="planned",
            **validated_data,
        )
        return walk
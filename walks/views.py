from datetime import datetime, timedelta, time

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Walk
from .serializers import WalkSerializer, WalkCreateSerializer
from animals.models import Animal
from users.models import VolunteerProfile
from users.api_guards import block_if_profile_blocked
from notifications.models import Notification, AdoptionRecommendation


def create_adoption_recommendation_if_needed(walk):
    completed_count = Walk.objects.filter(
        volunteer=walk.volunteer,
        animal=walk.animal,
        status="completed",
        ended_at__isnull=False
    ).count()

    if completed_count < 5:
        return

    recommendation, created = AdoptionRecommendation.objects.get_or_create(
        volunteer=walk.volunteer,
        animal=walk.animal,
        defaults={"walks_count": completed_count}
    )

    if created:
        Notification.objects.create(
            volunteer=walk.volunteer,
            title="Рекомендація щодо усиновлення",
            message=(
                f"Ви вже {completed_count} разів гуляли з {walk.animal.name}. "
                "Можливо, варто розглянути усиновлення цього песика?"
            )
        )


class WalkListAPIView(APIView):
    def get(self, request):
        status_filter = request.GET.get("status")
        volunteer_id = request.GET.get("volunteer")

        if not volunteer_id:
            return Response(
                {"detail": "Потрібно передати volunteer id"},
                status=400
            )

        blocked_response = block_if_profile_blocked(volunteer_id)
        if blocked_response:
            return blocked_response

        walks = Walk.objects.filter(
            volunteer_id=volunteer_id
        ).order_by("-planned_date", "-planned_start_time")

        if status_filter:
            walks = walks.filter(status=status_filter)

        serializer = WalkSerializer(
            walks,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)


class WalkDetailAPIView(APIView):
    def get(self, request, pk):
        walk = get_object_or_404(Walk, pk=pk)
        serializer = WalkSerializer(walk, context={"request": request})
        return Response(serializer.data)


class CreateWalkAPIView(APIView):
    def post(self, request):
        volunteer_id = request.data.get("volunteer")

        if not volunteer_id:
            return Response(
                {"volunteer": "Потрібно передати volunteer id."},
                status=status.HTTP_400_BAD_REQUEST
            )

        blocked_response = block_if_profile_blocked(volunteer_id)
        if blocked_response:
            return blocked_response

        volunteer = get_object_or_404(VolunteerProfile, pk=volunteer_id)

        serializer = WalkCreateSerializer(
            data=request.data,
            context={"volunteer": volunteer}
        )

        if serializer.is_valid():
            walk = serializer.save()
            return Response(
                WalkSerializer(walk, context={"request": request}).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AvailableAnimalsAPIView(APIView):
    def get(self, request):
        date_str = request.GET.get("date")

        if not date_str:
            return Response(
                {"detail": "Потрібно передати date у форматі YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"detail": "Некоректний формат date. Потрібно YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )

        busy_animal_ids = Walk.objects.filter(
            planned_date=selected_date
        ).values_list("animal_id", flat=True)

        animals = Animal.objects.exclude(id__in=busy_animal_ids).order_by("name")

        data = [
            {
                "id": animal.id,
                "name": animal.name,
                "breed": getattr(animal, "breed", ""),
            }
            for animal in animals
        ]

        return Response(data)


class AvailableDatesForAnimalAPIView(APIView):
    def get(self, request, animal_id):
        animal = get_object_or_404(Animal, pk=animal_id)

        today = timezone.localdate()
        result = []

        for i in range(14):
            current_date = today + timedelta(days=i)

            has_walk = Walk.objects.filter(
                animal=animal,
                planned_date=current_date
            ).exists()

            if not has_walk:
                result.append(str(current_date))

        return Response(result)


class AvailableSlotsForAnimalAPIView(APIView):
    def get(self, request, animal_id):
        animal = get_object_or_404(Animal, pk=animal_id)
        date_str = request.GET.get("date")

        if not date_str:
            return Response(
                {"detail": "Потрібно передати date у форматі YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"detail": "Некоректний формат date. Потрібно YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )

        has_walk = Walk.objects.filter(
            animal=animal,
            planned_date=selected_date
        ).exists()

        if has_walk:
            return Response([])

        slots = [
            {"start": "10:00", "durations": [30, 40]},
            {"start": "10:40", "durations": [30, 40]},
            {"start": "11:20", "durations": [30, 40]},
            {"start": "12:00", "durations": [30, 40]},
            {"start": "12:40", "durations": [30, 40]},
            {"start": "13:20", "durations": [30, 40]},
            {"start": "14:00", "durations": [30, 40]},
            {"start": "14:40", "durations": [30, 40]},
            {"start": "15:20", "durations": [30, 40]},
            {"start": "16:00", "durations": [30, 40]},
            {"start": "16:30", "durations": [30]},
        ]

        return Response(slots)


class StartWalkAPIView(APIView):
    def post(self, request, pk):
        walk = get_object_or_404(Walk, pk=pk)

        blocked_response = block_if_profile_blocked(walk.volunteer.id)
        if blocked_response:
            return blocked_response

        if walk.status != "planned":
            return Response(
                {"detail": "Почати можна тільки заплановану прогулянку."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not walk.planned_date or not walk.planned_start_time:
            return Response(
                {"detail": "У прогулянки відсутні заплановані дата або час."},
                status=status.HTTP_400_BAD_REQUEST
            )

        walk.status = "active"
        walk.started_at = timezone.now()
        walk.save()

        serializer = WalkSerializer(walk, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompleteWalkAPIView(APIView):
    def post(self, request, pk):
        walk = get_object_or_404(Walk, pk=pk)

        blocked_response = block_if_profile_blocked(walk.volunteer.id)
        if blocked_response:
            return blocked_response

        if walk.status != "active":
            return Response(
                {"detail": "Завершити можна тільки активну прогулянку."},
                status=status.HTTP_400_BAD_REQUEST
            )

        walk.status = "completed"
        walk.ended_at = timezone.now()
        walk.final_activity_score = request.data.get("final_activity_score")
        walk.unexpected_situations_comment = request.data.get(
            "unexpected_situations_comment", ""
        )
        walk.character_match_comment = request.data.get(
            "character_match_comment", ""
        )
        walk.overall_impression = request.data.get("overall_impression")

        completion_photo = request.FILES.get("completion_photo")
        if completion_photo:
            walk.completion_photo = completion_photo

        walk.save()

        create_adoption_recommendation_if_needed(walk)

        serializer = WalkSerializer(walk, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
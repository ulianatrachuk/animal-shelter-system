from django.urls import path
from .views import (
    WalkListAPIView,
    WalkDetailAPIView,
    CreateWalkAPIView,
    AvailableAnimalsAPIView,
    AvailableDatesForAnimalAPIView,
    AvailableSlotsForAnimalAPIView,
    StartWalkAPIView,
    CompleteWalkAPIView,
)

urlpatterns = [
    path("", WalkListAPIView.as_view(), name="walk-list"),

    # спочатку специфічні
    path("create/", CreateWalkAPIView.as_view(), name="walk-create"),
    path("available-animals/", AvailableAnimalsAPIView.as_view(), name="available-animals"),
    path("animal/<int:animal_id>/available-dates/", AvailableDatesForAnimalAPIView.as_view(), name="animal-available-dates"),
    path("animal/<int:animal_id>/available-slots/", AvailableSlotsForAnimalAPIView.as_view(), name="animal-available-slots"),

    # потім загальні
    path("<int:pk>/", WalkDetailAPIView.as_view(), name="walk-detail"),
    path("<int:pk>/start/", StartWalkAPIView.as_view(), name="walk-start"),
    path("<int:pk>/complete/", CompleteWalkAPIView.as_view(), name="walk-complete"),
]
from django.urls import path
from .views import (
    BehaviorTraitListAPIView,
    BehaviorReviewListAPIView,
    BehaviorReviewCreateAPIView,
    BehaviorReviewDetailAPIView,
    AnimalSpecificTraitsByAnimalAPIView,
    AnimalSpecificTraitReviewCreateAPIView,
    BehaviorCommentCreateAPIView,
)

urlpatterns = [
    path("traits/", BehaviorTraitListAPIView.as_view()),
    path("", BehaviorReviewListAPIView.as_view()),
    path("create/", BehaviorReviewCreateAPIView.as_view()),
    path("<int:pk>/", BehaviorReviewDetailAPIView.as_view()),
    path("animals/<int:animal_id>/specific-traits/", AnimalSpecificTraitsByAnimalAPIView.as_view(), name="animal-specific-traits", ),
    path("specific-trait-reviews/create/", AnimalSpecificTraitReviewCreateAPIView.as_view(),name="specific-trait-review-create", ),
    path("comment/create/", BehaviorCommentCreateAPIView.as_view()),
]
from django.urls import path
from .views import AnimalListAPIView, AnimalDetailAPIView

urlpatterns = [
    path("", AnimalListAPIView.as_view()),
    path("<int:pk>/", AnimalDetailAPIView.as_view()),
]
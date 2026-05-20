from django.urls import path
from .views import ChatMessageListCreateAPIView

urlpatterns = [
    path("messages/<int:profile_id>/", ChatMessageListCreateAPIView.as_view()),
]
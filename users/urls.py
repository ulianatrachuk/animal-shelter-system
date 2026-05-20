from django.urls import path
from .views import (
    RegisterAPIView,
    LoginAPIView,
    VolunteerProfileDetailAPIView,
    VolunteerProfileUpdateAPIView,
    ChangePasswordAPIView,
    DeleteProfileAPIView,
    DeleteProfilePhotoAPIView,
    VolunteerPreferenceListAPIView,
    VolunteerPreferenceUpdateAPIView,
)

urlpatterns = [
    path("register/", RegisterAPIView.as_view()),
    path("login/", LoginAPIView.as_view()),

    path("<int:pk>/", VolunteerProfileDetailAPIView.as_view()),
    path("<int:pk>/update/", VolunteerProfileUpdateAPIView.as_view()),
    path("<int:pk>/change-password/", ChangePasswordAPIView.as_view()),
    path("<int:pk>/delete/", DeleteProfileAPIView.as_view()),
    path("<int:pk>/photo/", DeleteProfilePhotoAPIView.as_view()),

    path("<int:profile_id>/preferences/", VolunteerPreferenceListAPIView.as_view()),
    path("preferences/<int:pk>/update/", VolunteerPreferenceUpdateAPIView.as_view()),
]
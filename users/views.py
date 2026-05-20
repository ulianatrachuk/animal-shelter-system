from django.shortcuts import get_object_or_404
from django.contrib.auth import login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from walks.services import check_missed_walks

from .models import VolunteerProfile, VolunteerPreference
from .serializers import (
    VolunteerProfileSerializer,
    VolunteerProfileUpdateSerializer,
    VolunteerPreferenceSerializer,
    VolunteerPreferenceUpdateSerializer,
    RegisterSerializer,
    LoginSerializer,
)


class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            profile = serializer.save()
            return Response(
                {
                    "message": "Користувача створено",
                    "profile_id": profile.id,
                    "full_name": profile.get_full_name(),
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    def post(self, request):
        check_missed_walks()

        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            profile = getattr(user, "volunteer_profile", None)

            if not profile:
                return Response(
                    {"error": "Профіль не знайдено"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if profile.is_blocked:
                return Response(
                    {
                        "error": "Ваш профіль заблоковано. Зверніться до адміністратора."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            login(request, user)

            return Response(
                {
                    "message": "Вхід успішний",
                    "profile_id": profile.id,
                    "full_name": profile.get_full_name(),
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VolunteerProfileDetailAPIView(APIView):
    def get(self, request, pk):
        # 🔥 перевірка пропущених прогулянок
        check_missed_walks()

        profile = get_object_or_404(VolunteerProfile, pk=pk)

        # 🔒 якщо користувач заблокований
        if profile.is_blocked:
            return Response(
                {
                    "detail": "Ваш профіль заблоковано. Зверніться до адміністратора."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = VolunteerProfileSerializer(
            profile,
            context={"request": request}
        )

        return Response(serializer.data)


class VolunteerProfileUpdateAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def patch(self, request, pk):
        profile = get_object_or_404(VolunteerProfile, pk=pk)
        serializer = VolunteerProfileUpdateSerializer(
            profile,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            output = VolunteerProfileSerializer(profile, context={"request": request})
            return Response(output.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordAPIView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, pk):
        profile = get_object_or_404(VolunteerProfile, pk=pk)

        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not current_password or not new_password:
            return Response(
                {"detail": "Заповни всі поля"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = profile.user

        if not user.check_password(current_password):
            return Response(
                {"detail": "Поточний пароль неправильний"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"detail": "Пароль змінено"},
            status=status.HTTP_200_OK,
        )


class DeleteProfileAPIView(APIView):
    def delete(self, request, pk):
        profile = get_object_or_404(VolunteerProfile, pk=pk)
        user = profile.user

        if profile.profile_photo:
            profile.profile_photo.delete(save=False)

        profile.delete()
        user.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class DeleteProfilePhotoAPIView(APIView):
    def delete(self, request, pk):
        profile = get_object_or_404(VolunteerProfile, pk=pk)

        if profile.profile_photo:
            profile.profile_photo.delete(save=False)
            profile.profile_photo = None
            profile.save()

        serializer = VolunteerProfileSerializer(profile, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class VolunteerPreferenceListAPIView(APIView):
    def get(self, request, profile_id):
        preferences = VolunteerPreference.objects.filter(volunteer_id=profile_id)
        serializer = VolunteerPreferenceSerializer(preferences, many=True)
        return Response(serializer.data)


class VolunteerPreferenceUpdateAPIView(APIView):
    def patch(self, request, pk):
        preference = get_object_or_404(VolunteerPreference, pk=pk)
        serializer = VolunteerPreferenceUpdateSerializer(
            preference,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
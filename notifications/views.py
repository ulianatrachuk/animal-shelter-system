from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users.models import VolunteerProfile
from .models import Notification, AdminAlert
from .serializers import NotificationSerializer, AdminAlertSerializer


class NotificationListAPIView(APIView):
    def get(self, request, profile_id):
        volunteer = get_object_or_404(VolunteerProfile, pk=profile_id)

        notifications = Notification.objects.filter(
            volunteer=volunteer
        ).order_by("-created_at")

        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MarkNotificationReadAPIView(APIView):
    def patch(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk)
        notification.is_read = True
        notification.save()

        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminAlertListAPIView(APIView):
    def get(self, request):
        alerts = AdminAlert.objects.filter(
            is_resolved=False
        ).order_by("-created_at")

        serializer = AdminAlertSerializer(alerts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ResolveAdminAlertAPIView(APIView):
    def patch(self, request, pk):
        alert = get_object_or_404(AdminAlert, pk=pk)
        alert.is_resolved = True
        alert.save()

        serializer = AdminAlertSerializer(alert)
        return Response(serializer.data, status=status.HTTP_200_OK)
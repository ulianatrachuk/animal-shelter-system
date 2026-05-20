from rest_framework import serializers
from .models import Notification, AdminAlert


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "is_read",
            "created_at",
        ]


class AdminAlertSerializer(serializers.ModelSerializer):
    volunteer_name = serializers.CharField(
        source="volunteer.get_full_name",
        read_only=True
    )

    class Meta:
        model = AdminAlert
        fields = [
            "id",
            "volunteer",
            "volunteer_name",
            "title",
            "message",
            "is_resolved",
            "created_at",
        ]
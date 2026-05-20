from rest_framework import serializers
from .models import ChatRoom, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "room",
            "text",
            "image",
            "image_url",
            "is_from_admin",
            "created_at",
        ]
        read_only_fields = ["image_url"]

    def get_image_url(self, obj):
        request = self.context.get("request")

        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)

        if obj.image:
            return obj.image.url

        return None


class ChatRoomSerializer(serializers.ModelSerializer):
    volunteer_name = serializers.SerializerMethodField()
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = ["id", "volunteer", "volunteer_name", "created_at", "messages"]

    def get_volunteer_name(self, obj):
        return obj.volunteer.get_full_name()
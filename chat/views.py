from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from users.models import VolunteerProfile
from .models import ChatRoom, ChatMessage
from .serializers import ChatMessageSerializer


class ChatMessageListCreateAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, profile_id):
        profile = VolunteerProfile.objects.get(id=profile_id)
        room, created = ChatRoom.objects.get_or_create(volunteer=profile)

        messages = room.messages.all()
        serializer = ChatMessageSerializer(
            messages,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)

    def post(self, request, profile_id):
        profile = VolunteerProfile.objects.get(id=profile_id)
        room, created = ChatRoom.objects.get_or_create(volunteer=profile)

        text = request.data.get("text", "").strip()
        image = request.FILES.get("image")

        if not text and not image:
            return Response(
                {"detail": "Повідомлення не може бути порожнім"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        message = ChatMessage.objects.create(
            room=room,
            text=text,
            image=image,
            is_from_admin=False,
        )

        serializer = ChatMessageSerializer(
            message,
            context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
from django.db import models
from users.models import VolunteerProfile


class ChatRoom(models.Model):
    volunteer = models.OneToOneField(
        VolunteerProfile,
        on_delete=models.CASCADE,
        related_name="chat_room"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Чат #{self.id} — {self.volunteer.get_full_name()}"


class ChatMessage(models.Model):
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    text = models.TextField(blank=True)
    image = models.ImageField(
        upload_to="chat/images/",
        null=True,
        blank=True
    )
    is_from_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        if self.text:
            return f"{self.room.volunteer.get_full_name()} — {self.text[:30]}"
        return f"{self.room.volunteer.get_full_name()} — фото"
from rest_framework import serializers
from .models import Animal


class AnimalSerializer(serializers.ModelSerializer):
    behavior_stats = serializers.SerializerMethodField()
    sex_display = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()
    specific_trait_stats = serializers.SerializerMethodField()

    class Meta:
        model = Animal
        fields = [
            "id",
            "name",
            "breed",
            "age",
            "sex",
            "sex_display",
            "health_status",
            "short_description",
            "photo_url",
            "behavior_stats",
            "specific_trait_stats",
        ]

    def get_behavior_stats(self, obj):
        return obj.get_behavior_stats()
    
    def get_specific_trait_stats(self, obj):
        return obj.get_specific_trait_stats()

    def get_sex_display(self, obj):
        return obj.get_sex_display()

    def get_photo_url(self, obj):
        request = self.context.get("request")
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        elif obj.photo:
            return obj.photo.url
        return None
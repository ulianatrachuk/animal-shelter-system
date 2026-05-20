from rest_framework import serializers
from .models import BehaviorTrait, BehaviorReview, BehaviorComment
from .models import AnimalSpecificTrait, AnimalSpecificTraitReview

class BehaviorTraitSerializer(serializers.ModelSerializer):
    class Meta:
        model = BehaviorTrait
        fields = ["id", "name", "description", "is_active"]


class BehaviorReviewSerializer(serializers.ModelSerializer):
    trait_name = serializers.CharField(source="trait.name", read_only=True)
    animal_name = serializers.CharField(source="animal.name", read_only=True)
    volunteer_name = serializers.CharField(source="volunteer.full_name", read_only=True)

    class Meta:
        model = BehaviorReview
        fields = [
            "id",
            "animal",
            "animal_name",
            "walk",
            "volunteer",
            "volunteer_name",
            "trait",
            "trait_name",
            "score",
            "created_at",
        ]

class BehaviorCommentSerializer(serializers.ModelSerializer):
    animal_name = serializers.CharField(source="animal.name", read_only=True)
    volunteer_name = serializers.CharField(source="volunteer.get_full_name", read_only=True)

    class Meta:
        model = BehaviorComment
        fields = [
            "id",
            "animal",
            "animal_name",
            "walk",
            "volunteer",
            "volunteer_name",
            "comment",
            "created_at",
        ]

class AnimalSpecificTraitSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalSpecificTrait
        fields = ["id", "animal", "name"]


class AnimalSpecificTraitReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalSpecificTraitReview
        fields = [
            "id",
            "animal",
            "walk",
            "volunteer",
            "trait",
            "answer",
            "created_at",
        ]
        read_only_fields = ["created_at"]
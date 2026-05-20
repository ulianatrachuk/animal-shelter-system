from rest_framework import serializers
from django.contrib.auth.models import User
from .models import VolunteerProfile, VolunteerPreference
from django.contrib.auth import authenticate


class VolunteerPreferenceSerializer(serializers.ModelSerializer):
    criterion_name = serializers.CharField(source="criterion.name", read_only=True)

    class Meta:
        model = VolunteerPreference
        fields = ["id", "criterion", "criterion_name", "is_enabled"]


class VolunteerProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.SerializerMethodField()
    walks_count = serializers.SerializerMethodField()
    favorite_dog = serializers.SerializerMethodField()
    preferences = VolunteerPreferenceSerializer(many=True, read_only=True)
    profile_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = VolunteerProfile
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone",
            "birth_date",
            "profile_photo_url",
            "walks_count",
            "favorite_dog",
            "preferences",
            "is_blocked",
            "block_reason",
            "missed_walks_count",
            "blocked_at",
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_walks_count(self, obj):
        return obj.get_completed_walks_count()

    def get_favorite_dog(self, obj):
        return obj.get_favorite_completed_dog()

    def get_profile_photo_url(self, obj):
        request = self.context.get("request")
        if obj.profile_photo and request:
            return request.build_absolute_uri(obj.profile_photo.url)
        elif obj.profile_photo:
            return obj.profile_photo.url
        return None


class VolunteerProfileUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True, required=False)

    class Meta:
        model = VolunteerProfile
        fields = [
            "first_name",
            "last_name",
            "phone",
            "birth_date",
            "profile_photo",
            "email",
        ]

    def update(self, instance, validated_data):
        email = validated_data.pop("email", None)

        if email is not None:
            instance.user.email = email
            instance.user.username = email
            instance.user.save()

        return super().update(instance, validated_data)


class VolunteerPreferenceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerPreference
        fields = ["id", "criterion", "is_enabled"]


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    birth_date = serializers.DateField(required=False, allow_null=True)

    def validate_email(self, value):
        if User.objects.filter(username=value).exists() or User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Користувач з таким email вже існує.")
        return value

    def validate_phone(self, value):
        if VolunteerProfile.objects.filter(phone=value).exists():
            raise serializers.ValidationError(
                "Користувач з таким номером телефону вже існує."
            )
        return value

    def create(self, validated_data):
        email = validated_data["email"]

        user = User.objects.create_user(
            username=email,
            email=email,
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )

        profile = VolunteerProfile.objects.create(
            user=user,
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone=validated_data["phone"],
            birth_date=validated_data.get("birth_date")
        )

        return profile
    
class LoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email_or_phone = attrs.get("email_or_phone")
        password = attrs.get("password")

        user = None

        # Спроба входу через email (username у тебе = email)
        user = authenticate(username=email_or_phone, password=password)

        # Якщо не вийшло — спроба через телефон
        if user is None:
            try:
                profile = VolunteerProfile.objects.get(phone=email_or_phone)
                user = authenticate(username=profile.user.username, password=password)
            except VolunteerProfile.DoesNotExist:
                pass

        if user is None:
            raise serializers.ValidationError("Неправильний email/номер телефону або пароль.")

        attrs["user"] = user
        return attrs
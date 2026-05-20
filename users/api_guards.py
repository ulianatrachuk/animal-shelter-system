from rest_framework.response import Response
from rest_framework import status

from users.models import VolunteerProfile


def get_blocked_response():
    return Response(
        {
            "detail": "Ваш профіль заблоковано. Зверніться до адміністратора."
        },
        status=status.HTTP_403_FORBIDDEN
    )


def block_if_profile_blocked(profile_id):
    if not profile_id:
        return None

    try:
        profile = VolunteerProfile.objects.get(id=profile_id)
    except VolunteerProfile.DoesNotExist:
        return None

    if profile.is_blocked:
        return get_blocked_response()

    return None
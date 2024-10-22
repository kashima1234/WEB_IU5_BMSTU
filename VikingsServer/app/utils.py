from app.jwt_helper import get_session, get_session_payload
from app.models import User
from django.core.cache import cache


def identity_user(request):
    session = get_session(request)

    if session is None or session not in cache:
        return False

    payload = get_session_payload(session)
    user_id = payload["user_id"]
    user = User.objects.get(pk=user_id)

    return user


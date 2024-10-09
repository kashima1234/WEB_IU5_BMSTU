from app.jwt_helper import get_access_token, get_jwt_payload
from app.models import User
from django.core.cache import cache


def identity_user(request):
    token = get_access_token(request)

    if token is None:
        return None

    if token in cache:
        return None

    try:
        payload = get_jwt_payload(token)
        user_id = payload["user_id"]
        user = User.objects.get(pk=user_id)

        return user
    except:
        pass

    return None
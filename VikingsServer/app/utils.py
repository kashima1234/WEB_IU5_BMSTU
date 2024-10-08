import random

from app.jwt_helper import get_access_token, get_jwt_payload
from app.models import User


def identity_user(request):
    access_token = get_access_token(request)

    if access_token is None:
        return None

    try:
        payload = get_jwt_payload(access_token)
        user_id = payload["user_id"]
        user = User.objects.get(pk=user_id)

        return user

    except:
        return None

    return None


def random_text():
    words = ["lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit", "cras", "eu", "blandit",
           "lacus",  "vivamus", "tincidunt", "ante", "nec", "nunc", "tincidunt", "lacinia", "curabitur", "maximus",
           "vulputate", "nisi", "vitae", "bibendum"]

    text = ""

    for _ in range(random.randint(1, 10)):
        text += random.choice(words) + " "

    text = text.strip().replace(text[0], text[0].upper(), 1)

    return text
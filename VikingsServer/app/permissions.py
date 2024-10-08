from django.contrib.auth.models import User
from django.core.cache import cache
from rest_framework.permissions import BasePermission

from .jwt_helper import get_jwt_payload, get_access_token


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        token = get_access_token(request)

        if token is None:
            return False

        if token in cache:
            return None

        try:
            payload = get_jwt_payload(token)
        except:
            return False

        try:
            user = User.objects.get(pk=payload["user_id"])
        except:
            return False

        return user.is_active


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        token = get_access_token(request)

        if token is None:
            return False

        if token in cache:
            return None

        try:
            payload = get_jwt_payload(token)
        except:
            return False

        try:
            user = User.objects.get(pk=payload["user_id"])
        except:
            return False

        return user.is_staff

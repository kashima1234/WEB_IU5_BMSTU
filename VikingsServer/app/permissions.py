from django.contrib.auth.models import User
from django.core.cache import cache
from rest_framework.permissions import BasePermission

from .jwt_helper import get_session_payload, get_session


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        session = get_session(request)

        if session is None or session not in cache:
            return False

        try:
            payload = get_session_payload(session)
        except:
            return False

        try:
            user = User.objects.get(pk=payload["user_id"])
        except:
            return False

        return user.is_active


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        session = get_session(request)

        if session is None or session not in cache:
            return False

        try:
            payload = get_session_payload(session)
        except:
            return False

        try:
            user = User.objects.get(pk=payload["user_id"])
        except:
            return False

        return user.is_staff

import random
from datetime import datetime, timedelta
import uuid

from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .permissions import *
from .redis import session_storage
from .serializers import *
from .utils import identity_user, get_session


def get_draft_expedition(request):
    user = identity_user(request)

    if user is None:
        return None

    expedition = Expedition.objects.filter(owner=user).filter(status=1).first()

    return expedition


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'place_name',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
def search_places(request):
    place_name = request.GET.get("place_name", "")

    places = Place.objects.filter(status=1)

    if place_name:
        places = places.filter(name__icontains=place_name)

    serializer = PlacesSerializer(places, many=True)

    draft_expedition = get_draft_expedition(request)

    resp = {
        "places": serializer.data,
        "places_count": PlaceExpedition.objects.filter(expedition=draft_expedition).count() if draft_expedition else None,
        "draft_expedition_id": draft_expedition.pk if draft_expedition else None
    }

    return Response(resp)


@api_view(["GET"])
def get_place_by_id(request, place_id):
    if not Place.objects.filter(pk=place_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    place = Place.objects.get(pk=place_id)
    serializer = PlaceSerializer(place)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=PlaceSerializer)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_place(request, place_id):
    if not Place.objects.filter(pk=place_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    place = Place.objects.get(pk=place_id)

    serializer = PlaceSerializer(place, data=request.data)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='POST', request_body=PlaceAddSerializer)
@api_view(["POST"])
@permission_classes([IsModerator])
@parser_classes((MultiPartParser,))
def create_place(request):
    serializer = PlaceAddSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    Place.objects.create(**serializer.validated_data)

    places = Place.objects.filter(status=1)
    serializer = PlacesSerializer(places, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsModerator])
def delete_place(request, place_id):
    if not Place.objects.filter(pk=place_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    place = Place.objects.get(pk=place_id)
    place.status = 2
    place.save()

    place = Place.objects.filter(status=1)
    serializer = PlaceSerializer(place, many=True)

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_place_to_expedition(request, place_id):
    if not Place.objects.filter(pk=place_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    place = Place.objects.get(pk=place_id)

    draft_expedition = get_draft_expedition(request)

    if draft_expedition is None:
        draft_expedition = Expedition.objects.create()
        draft_expedition.date_created = timezone.now()
        draft_expedition.owner = identity_user(request)
        draft_expedition.save()

    if PlaceExpedition.objects.filter(expedition=draft_expedition, place=place).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    item = PlaceExpedition.objects.create()
    item.expedition = draft_expedition
    item.place = place
    item.save()

    serializer = ExpeditionSerializer(draft_expedition)
    return Response(serializer.data["places"])


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE),
    ]
)
@api_view(["POST"])
@permission_classes([IsModerator])
@parser_classes((MultiPartParser,))
def update_place_image(request, place_id):
    if not Place.objects.filter(pk=place_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    place = Place.objects.get(pk=place_id)

    image = request.data.get("image")

    if image is None:
        return Response(status.HTTP_400_BAD_REQUEST)

    place.image = image
    place.save()

    serializer = PlaceSerializer(place)

    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            type=openapi.TYPE_NUMBER
        ),
        openapi.Parameter(
            'date_formation_start',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'date_formation_end',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_expeditions(request):
    status_id = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    expeditions = Expedition.objects.exclude(status__in=[1, 5])

    user = identity_user(request)
    if not user.is_superuser:
        expeditions = expeditions.filter(owner=user)

    if status_id > 0:
        expeditions = expeditions.filter(status=status_id)

    if date_formation_start and parse_datetime(date_formation_start):
        expeditions = expeditions.filter(date_formation__gte=parse_datetime(date_formation_start) - timedelta(days=1))

    if date_formation_end and parse_datetime(date_formation_end):
        expeditions = expeditions.filter(date_formation__lt=parse_datetime(date_formation_end) + timedelta(days=1))

    serializer = ExpeditionsSerializer(expeditions, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_expedition_by_id(request, expedition_id):
    user = identity_user(request)

    if not Expedition.objects.filter(pk=expedition_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    expedition = Expedition.objects.get(pk=expedition_id)

    if not user.is_superuser and expedition.owner != user:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ExpeditionSerializer(expedition)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=ExpeditionSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_expedition(request, expedition_id):
    user = identity_user(request)

    if not Expedition.objects.filter(pk=expedition_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    expedition = Expedition.objects.get(pk=expedition_id)
    serializer = ExpeditionSerializer(expedition, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_status_user(request, expedition_id):
    user = identity_user(request)

    if not Expedition.objects.filter(pk=expedition_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    expedition = Expedition.objects.get(pk=expedition_id)

    if expedition.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    expedition.status = 2
    expedition.date_formation = timezone.now()
    expedition.save()

    serializer = ExpeditionSerializer(expedition)

    return Response(serializer.data)


def random_date():
    now = datetime.now(tz=timezone.utc)
    return now + timedelta(random.uniform(-1, 0) * 100)


@swagger_auto_schema(method='put', request_body=UpdateExpeditionStatusAdminSerializer)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_status_admin(request, expedition_id):
    if not Expedition.objects.filter(pk=expedition_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    expedition = Expedition.objects.get(pk=expedition_id)

    if expedition.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request_status == 3:
        expedition.date = random_date()

    expedition.status = request_status
    expedition.date_complete = timezone.now()
    expedition.moderator = identity_user(request)
    expedition.save()

    serializer = ExpeditionSerializer(expedition)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_expedition(request, expedition_id):
    user = identity_user(request)

    if not Expedition.objects.filter(pk=expedition_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    expedition = Expedition.objects.get(pk=expedition_id)

    if expedition.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    expedition.status = 5
    expedition.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_place_from_expedition(request, expedition_id, place_id):
    user = identity_user(request)

    if not Expedition.objects.filter(pk=expedition_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not PlaceExpedition.objects.filter(expedition_id=expedition_id, place_id=place_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = PlaceExpedition.objects.get(expedition_id=expedition_id, place_id=place_id)
    item.delete()

    expedition = Expedition.objects.get(pk=expedition_id)

    serializer = ExpeditionSerializer(expedition)
    places = serializer.data["places"]

    return Response(places)


@swagger_auto_schema(method='PUT', request_body=PlaceExpeditionSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_place_in_expedition(request, expedition_id, place_id):
    user = identity_user(request)

    if not Expedition.objects.filter(pk=expedition_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not PlaceExpedition.objects.filter(place_id=place_id, expedition_id=expedition_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = PlaceExpedition.objects.get(place_id=place_id, expedition_id=expedition_id)

    serializer = PlaceExpeditionSerializer(item, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_200_OK)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@swagger_auto_schema(method='post', request_body=UserRegisterSerializer)
@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_201_CREATED)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    session = get_session(request)
    session_storage.delete(session)

    response = Response(status=status.HTTP_200_OK)
    response.delete_cookie('session_id')

    return response


@swagger_auto_schema(method='PUT', request_body=UserProfileSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = identity_user(request)

    if user.pk != user_id:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    password = request.data.get("password", None)
    if password is not None and not user.check_password(password):
        user.set_password(password)
        user.save()

    return Response(serializer.data, status=status.HTTP_200_OK)

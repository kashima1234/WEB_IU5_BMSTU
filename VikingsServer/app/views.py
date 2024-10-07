import requests
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import *


def get_draft_expedition():
    return Expedition.objects.filter(status=1).first()


def get_user():
    return User.objects.filter(is_superuser=False).first()


def get_moderator():
    return User.objects.filter(is_superuser=True).first()


@api_view(["GET"])
def search_places(request):
    query = request.GET.get("query", "")

    places = Place.objects.filter(status=1).filter(name__icontains=query)

    serializer = PlaceSerializer(places, many=True)

    draft_expedition = get_draft_expedition()

    resp = {
        "places": serializer.data,
        "places_count": len(serializer.data),
        "draft_expedition": draft_expedition.pk if draft_expedition else None
    }

    return Response(resp)


@api_view(["GET"])
def get_place_by_id(request, place_id):
    if not Place.objects.filter(pk=place_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    place = Place.objects.get(pk=place_id)
    serializer = PlaceSerializer(place, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_place(request, place_id):
    if not Place.objects.filter(pk=place_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    place = Place.objects.get(pk=place_id)

    image = request.data.get("image")
    if image is not None:
        place.image = image
        place.save()

    serializer = PlaceSerializer(place, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def create_place(request):
    Place.objects.create()

    places = Place.objects.filter(status=1)
    serializer = PlaceSerializer(places, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_place(request, place_id):
    if not Place.objects.filter(pk=place_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    place = Place.objects.get(pk=place_id)
    place.status = 2
    place.save()

    places = Place.objects.filter(status=1)
    serializer = PlaceSerializer(places, many=True)

    return Response(serializer.data)


@api_view(["POST"])
def add_place_to_expedition(request, place_id):
    if not Place.objects.filter(pk=place_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    place = Place.objects.get(pk=place_id)

    draft_expedition = get_draft_expedition()

    if draft_expedition is None:
        draft_expedition = Expedition.objects.create()
        draft_expedition.owner = get_user()
        draft_expedition.date_created = timezone.now()
        draft_expedition.save()

    if PlaceExpedition.objects.filter(expedition=draft_expedition, place=place).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    item = PlaceExpedition.objects.create()
    item.expedition = draft_expedition
    item.place = place
    item.save()

    items = PlaceExpedition.objects.filter(expedition=draft_expedition)
    places = [PlaceSerializer(item.place, many=False).data for item in items]
    return Response(places)


@api_view(["POST"])
def update_place_image(request, place_id):
    if not Place.objects.filter(pk=place_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    place = Place.objects.get(pk=place_id)

    image = request.data.get("image")
    if image is not None:
        place.image = image
        place.save()

    serializer = PlaceSerializer(place)

    return Response(serializer.data)


@api_view(["GET"])
def search_expeditions(request):
    status = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    expeditions = Expedition.objects.exclude(status__in=[1, 5])

    if status > 0:
        expeditions = expeditions.filter(status=status)

    if date_formation_start and parse_datetime(date_formation_start):
        expeditions = expeditions.filter(date_formation__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        expeditions = expeditions.filter(date_formation__lt=parse_datetime(date_formation_end))

    serializer = ExpeditionsSerializer(expeditions, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_expedition_by_id(request, expedition_id):
    if not Expedition.objects.filter(pk=expedition_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    expedition = Expedition.objects.get(pk=expedition_id)
    serializer = ExpeditionSerializer(expedition, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_expedition(request, expedition_id):
    if not Expedition.objects.filter(pk=expedition_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    expedition = Expedition.objects.get(pk=expedition_id)
    serializer = ExpeditionSerializer(expedition, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_user(request, expedition_id):
    if not Expedition.objects.filter(pk=expedition_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    expedition = Expedition.objects.get(pk=expedition_id)

    if expedition.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    expedition.status = 2
    expedition.date_formation = timezone.now()
    expedition.save()

    serializer = ExpeditionSerializer(expedition, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_admin(request, expedition_id):
    if not Expedition.objects.filter(pk=expedition_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    expedition = Expedition.objects.get(pk=expedition_id)

    if expedition.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    expedition.date_complete = timezone.now()
    expedition.status = request_status
    expedition.moderator = get_moderator()
    expedition.save()

    serializer = ExpeditionSerializer(expedition, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_expedition(request, expedition_id):
    if not Expedition.objects.filter(pk=expedition_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    expedition = Expedition.objects.get(pk=expedition_id)

    if expedition.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    expedition.status = 5
    expedition.save()

    serializer = ExpeditionSerializer(expedition, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_place_from_expedition(request, expedition_id, place_id):
    if not PlaceExpedition.objects.filter(expedition_id=expedition_id, place_id=place_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = PlaceExpedition.objects.get(expedition_id=expedition_id, place_id=place_id)
    item.delete()

    expedition = Expedition.objects.get(pk=expedition_id)

    serializer = ExpeditionSerializer(expedition, many=False)
    places = serializer.data["places"]

    if len(places) == 0:
        expedition.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(places)


@api_view(["PUT"])
def update_place_in_expedition(request, expedition_id, place_id):
    if not PlaceExpedition.objects.filter(place_id=place_id, expedition_id=expedition_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = PlaceExpedition.objects.get(place_id=place_id, expedition_id=expedition_id)

    serializer = PlaceExpeditionSerializer(item, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def logout(request):
    return Response(status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(pk=user_id)
    serializer = UserSerializer(user, data=request.data, many=False, partial=True)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data)
from django.contrib.auth.models import User
from django.db import connection
from django.shortcuts import render, redirect
from django.utils import timezone

from app.models import Place, Expedition, PlaceExpedition


def index(request):
    place_name = request.GET.get("place_name", "")
    places = Place.objects.filter(status=1)

    if place_name:
        places = places.filter(name__icontains=place_name)

    draft_expedition = get_draft_expedition()

    context = {
        "place_name": place_name,
        "places": places
    }

    if draft_expedition:
        context["places_count"] = len(draft_expedition.get_places())
        context["draft_expedition"] = draft_expedition

    return render(request, "home_page.html", context)


def add_place_to_draft_expedition(request, place_id):
    place = Place.objects.get(pk=place_id)

    draft_expedition = get_draft_expedition()

    if draft_expedition is None:
        draft_expedition = Expedition.objects.create()
        draft_expedition.owner = get_current_user()
        draft_expedition.date_created = timezone.now()
        draft_expedition.save()

    if PlaceExpedition.objects.filter(expedition=draft_expedition, place=place).exists():
        return redirect("/")

    item = PlaceExpedition(
        expedition=draft_expedition,
        place=place
    )
    item.save()

    return redirect("/")


def place_details(request, place_id):
    context = {
        "place": Place.objects.get(id=place_id)
    }

    return render(request, "place_page.html", context)


def delete_expedition(request, expedition_id):
    if not Expedition.objects.filter(pk=expedition_id).exists():
        return redirect("/")

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM place_expedition WHERE expedition_id = %s", [expedition_id])
        cursor.execute("DELETE FROM expeditions WHERE id = %s", [expedition_id])

    return redirect("/")


def expedition(request, expedition_id):
    if not Expedition.objects.filter(pk=expedition_id).exists():
        return redirect("/")

    context = {
        "expedition": Expedition.objects.get(id=expedition_id),
    }

    return render(request, "expedition_page.html", context)


def get_draft_expedition():
    return Expedition.objects.filter(status=1).first()


def get_current_user():
    return User.objects.filter(is_superuser=False).first()
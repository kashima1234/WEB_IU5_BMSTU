from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('places/<int:place_id>/', place_details, name="place_details"),
    path('places/<int:place_id>/add_to_expedition/', add_place_to_draft_expedition, name="add_place_to_draft_expedition"),
    path('expeditions/<int:expedition_id>/delete/', delete_expedition, name="delete_expedition"),
    path('expeditions/<int:expedition_id>/', expedition)
]

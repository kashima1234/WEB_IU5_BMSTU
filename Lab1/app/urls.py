from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('places/<int:place_id>/', place),
    path('expeditions/<int:expedition_id>/', expedition),
]
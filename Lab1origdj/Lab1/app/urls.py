from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('citys/<int:city_id>/', city),
    path('expeditions/<int:expedition_id>/', expedition),
]
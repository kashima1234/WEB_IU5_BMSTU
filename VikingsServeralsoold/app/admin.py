from django.contrib import admin

from .models import *

admin.site.register(Place)
admin.site.register(Expedition)
admin.site.register(PlaceExpedition)

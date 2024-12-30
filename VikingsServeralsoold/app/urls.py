from django.urls import path
from .views import *

urlpatterns = [
    # Набор методов для услуг
    path('api/places/', search_places),  # GET
    path('api/places/<int:place_id>/', get_place_by_id),  # GET
    path('api/places/<int:place_id>/update/', update_place),  # PUT
    path('api/places/<int:place_id>/update_image/', update_place_image),  # POST
    path('api/places/<int:place_id>/delete/', delete_place),  # DELETE
    path('api/places/create/', create_place),  # POST
    path('api/places/<int:place_id>/add_to_expedition/', add_place_to_expedition),  # POST

    # Набор методов для заявок
    path('api/expeditions/', search_expeditions),  # GET
    path('api/expeditions/<int:expedition_id>/', get_expedition_by_id),  # GET
    path('api/expeditions/<int:expedition_id>/update/', update_expedition),  # PUT
    path('api/expeditions/<int:expedition_id>/update_status_user/', update_status_user),  # PUT
    path('api/expeditions/<int:expedition_id>/update_status_admin/', update_status_admin),  # PUT
    path('api/expeditions/<int:expedition_id>/delete/', delete_expedition),  # DELETE

    # Набор методов для м-м
    path('api/expeditions/<int:expedition_id>/update_place/<int:place_id>/', update_place_in_expedition),  # PUT
    path('api/expeditions/<int:expedition_id>/delete_place/<int:place_id>/', delete_place_from_expedition),  # DELETE

    # Набор методов для аутентификации и авторизации
    path("api/users/register/", register),  # POST
    path("api/users/login/", login),  # POST
    path("api/users/logout/", logout),  # POST
    path("api/users/<int:user_id>/update/", update_user)  # PUT
]

from rest_framework import serializers

from .models import *


class PlacesSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, place):
        if place.image:
            return place.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

    class Meta:
        model = Place
        fields = ("id", "name", "status", "square", "image")


class PlaceSerializer(PlacesSerializer):
    class Meta:
        model = Place
        fields = "__all__"


class PlaceAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ("name", "description", "square", "image")


class ExpeditionsSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    moderator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Expedition
        fields = "__all__"


class ExpeditionSerializer(ExpeditionsSerializer):
    places = serializers.SerializerMethodField()

    def get_places(self, expedition):
        items = PlaceExpedition.objects.filter(expedition=expedition)
        return [PlaceItemSerializer(item.place, context={"order": item.order}).data for item in items]


class PlaceItemSerializer(PlaceSerializer):
    order = serializers.SerializerMethodField()

    def get_order(self, _):
        return self.context.get("order")

    class Meta:
        model = Place
        fields = ("id", "name", "status", "square", "image", "order")


class PlaceExpeditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceExpedition
        fields = "__all__"


class UpdateExpeditionStatusAdminSerializer(serializers.Serializer):
    status = serializers.IntegerField(required=True)

    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', "is_superuser")


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class UserProfileSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    password = serializers.CharField(required=False)

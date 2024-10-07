from rest_framework import serializers

from .models import *


class PlaceSerializer(serializers.ModelSerializer):
    def get_image(self, place):
        return place.image.url.replace("minio", "localhost", 1)

    class Meta:
        model = Place
        fields = "__all__"


class ExpeditionSerializer(serializers.ModelSerializer):
    places = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()

    def get_owner(self, expedition):
        return expedition.owner.username

    def get_moderator(self, expedition):
        if expedition.moderator:
            return expedition.moderator.username
            
    def get_places(self, expedition):
        items = PlaceExpedition.objects.filter(expedition=expedition)
        return [{**PlaceSerializer(item.place).data, "value": item.value} for item in items]

    class Meta:
        model = Expedition
        fields = '__all__'


class ExpeditionsSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()

    def get_owner(self, expedition):
        return expedition.owner.username

    def get_moderator(self, expedition):
        if expedition.moderator:
            return expedition.moderator.username

    class Meta:
        model = Expedition
        fields = "__all__"


class PlaceExpeditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceExpedition
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name')


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

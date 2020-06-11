from rest_framework import serializers

from .models import User, Entity


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ["id", "slug", "user"]

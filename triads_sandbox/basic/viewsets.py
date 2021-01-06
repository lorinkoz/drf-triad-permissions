from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Entity, User  # noqa
from .policies import BasicPolicy, UserBasedPolicy  # noqa
from .serializers import EntitySerializer, UserSerializer  # noqa


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = BasicPolicy.expand()

    def perform_destroy(self, obj):
        pass  # To preserve objects while testing


class EntityByUserViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = UserBasedPolicy.expand()
    lookup_field = "slug"

    def get_queryset(self):
        return super().get_queryset().filter(user__username=self.kwargs["username"])

    def perform_destroy(self, obj):
        pass  # To preserve objects while testing

    @action(methods=["post"], detail=True)
    def poke(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

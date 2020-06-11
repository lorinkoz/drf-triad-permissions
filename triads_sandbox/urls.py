from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter
from drf_triad_permissions.views import triad_permissions_js

from basic import viewsets

router = DefaultRouter()


router.register("users", viewsets.UserViewSet)
router.register(r"entities-by-user/(?P<username>\w+)", viewsets.EntityByUserViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("permissions.js", triad_permissions_js, name="triad_permissions_js"),
    path("api/", include(router.urls)),
]

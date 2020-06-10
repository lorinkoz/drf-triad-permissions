from django.contrib import admin
from django.urls import path

from drf_triad_permissions.views import triad_permissions_js

urlpatterns = [
    path("admin/", admin.site.urls),
    path("permissions.js", triad_permissions_js, name="triad_permissions_js"),
]

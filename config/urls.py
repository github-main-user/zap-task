from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # admin
    path("admin/", admin.site.urls),
    # docs
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/docs/", SpectacularSwaggerView.as_view(), name="swagger-ui"),
    path("api/v1/redoc/", SpectacularRedocView.as_view(), name="redoc"),
    # apps
    path("api/v1/users/", include("apps.users.urls", namespace="users")),
    path("api/v1/tasks/", include("apps.tasks.urls", namespace="tasks")),
]

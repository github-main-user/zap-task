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
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(), name="redoc"),
    # apps
    path("api/users/", include("apps.users.urls", namespace="users")),
    path("api/tasks/", include("apps.tasks.urls", namespace="tasks")),
    path("api/reviews/", include("apps.reviews.urls", namespace="reviews")),
]

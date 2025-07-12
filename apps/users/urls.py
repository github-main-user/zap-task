from django.urls import path

from .views import (
    ChangePasswordView,
    DecoratedTokenObtainPairView,
    DecoratedTokenRefreshView,
    MeView,
    RegisterView,
    UserPublicDetail,
)

app_name = "users"


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("me/", MeView.as_view(), name="user-me"),
    path("<int:pk>/", UserPublicDetail.as_view(), name="user-public-detail"),
    path("token/", DecoratedTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", DecoratedTokenRefreshView.as_view(), name="token_refresh"),
]

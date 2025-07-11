import logging

from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    ChangePasswordSerializer,
    MeSerializer,
    RegisterSerializer,
    UserPublicSerializer,
)

logger = logging.getLogger(__name__)

User = get_user_model()


@extend_schema(
    summary="Register a new user",
    description="This endpoint allows anyone to register a new user account.",
    tags=["Users"],
)
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save()
        logger.info(f"User {user.email} registered successfully.")


@extend_schema(
    summary="Retrieve, update or delete current user",
    description="This endpoint allows authenticated users to retrieve, update, or "
    "delete their own user profile.",
    tags=["Users"],
)
class MeView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MeSerializer

    def get_object(self):
        return self.request.user


@extend_schema(
    summary="Retrieve public user details",
    description="This endpoint allows anyone to retrieve public details of a "
    "specific user.",
    tags=["Users"],
)
class UserPublicDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserPublicSerializer


@extend_schema(
    summary="Change user password",
    description="This endpoint allows authenticated users to change their password.",
    tags=["Users"],
)
class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not user.check_password(serializer.data.get("old_password")):
            return Response(
                {"old_password": ["Wrong password."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.data.get("new_password"))
        user.save()

        logger.info(f"User {user.email} changed password successfully.")
        return Response(status=status.HTTP_204_NO_CONTENT)

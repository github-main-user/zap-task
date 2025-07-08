from rest_framework.permissions import BasePermission

from .models import User


class IsClient(BasePermission):
    """
    Permission to check if the user is a client.
    """

    message = "You are not a client."

    def has_permission(self, request, view) -> bool:
        return request.user.role == User.UserRole.CLIENT


class IsFreelancer(BasePermission):
    """
    Permission to check if the user is a freelancer.
    """

    message = "You are not a freelancer."

    def has_permission(self, request, view) -> bool:
        return request.user.role == User.UserRole.FREELANCER

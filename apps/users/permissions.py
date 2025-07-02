from rest_framework.permissions import BasePermission

from .models import User


class IsClient(BasePermission):
    def has_permission(self, request, view) -> bool:
        return request.user.role == User.UserRoles.CLIENT


class IsFreelancer(BasePermission):
    def has_permission(self, request, view) -> bool:
        return request.user.role == User.UserRoles.FREELANCER

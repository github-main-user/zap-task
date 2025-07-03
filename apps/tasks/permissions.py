from rest_framework.permissions import BasePermission

from .models import Task


class IsTaskOpen(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.status == Task.TaskStatus.OPEN


class IsTaskOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.client == request.user

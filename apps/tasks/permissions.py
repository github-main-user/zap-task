from rest_framework.permissions import BasePermission

from .models import Task


class IsTaskOpen(BasePermission):
    def has_object_permission(self, request, view, task):
        return task.status == Task.TaskStatus.OPEN


class IsTaskInProgress(BasePermission):
    def has_object_permission(self, request, view, task):
        return task.status == Task.TaskStatus.IN_PROGRESS


class IsTaskPendingReview(BasePermission):
    def has_object_permission(self, request, view, task):
        return task.status == Task.TaskStatus.PENDING_REVIEW


class IsTaskOwner(BasePermission):
    def has_object_permission(self, request, view, task):
        return task.client == request.user


class IsTaskFreelancer(BasePermission):
    def has_object_permission(self, request, view, task):
        return task.freelancer == request.user

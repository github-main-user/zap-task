from rest_framework.permissions import BasePermission

from .models import Task


class IsTaskOpen(BasePermission):
    """Permission to check if the task is open."""

    message = "This task is not open."

    def has_object_permission(self, request, view, task):
        return task.status == Task.TaskStatus.OPEN


class IsTaskPaid(BasePermission):
    """Permission to check if the task is paid."""

    message = "This task is not paid."

    def has_object_permission(self, request, view, task):
        return task.status == Task.TaskStatus.PAID


class IsTaskInProgress(BasePermission):
    """Permission to check if the task is in progress."""

    message = "This task is not in progress."

    def has_object_permission(self, request, view, task):
        return task.status == Task.TaskStatus.IN_PROGRESS


class IsTaskPendingReview(BasePermission):
    """Permission to check if the task is pending review."""

    message = "This task is not pending review."

    def has_object_permission(self, request, view, task):
        return task.status == Task.TaskStatus.PENDING_REVIEW


class IsClientOfTask(BasePermission):
    """Permission to check if the user is the client of the task."""

    message = "You are not the client of this task."

    def has_object_permission(self, request, view, task):
        return task.client == request.user


class IsFreelancerOfTask(BasePermission):
    """Permission to check if the user is the freelancer of the task."""

    message = "You are not the freelancer of this task."

    def has_object_permission(self, request, view, task):
        return task.freelancer == request.user


class IsFreelancerAssingedToTask(BasePermission):
    """Permission to check if a freelancer assigned to the task."""

    message = "This task task no freelancer assigned"

    def has_object_permission(self, request, view, task):
        return task.freelancer is not None

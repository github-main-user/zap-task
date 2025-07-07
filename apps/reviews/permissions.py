from rest_framework.permissions import BasePermission

from apps.tasks.models import Task


class IsPartOfTask(BasePermission):
    def has_permission(self, request, view):
        task = view.get_task()
        return request.user in [task.client, task.freelancer]


class IsTaskCompleted(BasePermission):
    def has_permission(self, request, view):
        task = view.get_task()
        return task.status == Task.TaskStatus.COMPLETED


class IsFreelancerAssignedToTask(BasePermission):
    def has_permission(self, request, view):
        task = view.get_task()
        return task.freelancer is not None


class IsReviewOwner(BasePermission):
    def has_object_permission(self, request, view, review):
        return review.reviewer == request.user

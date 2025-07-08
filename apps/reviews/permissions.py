from rest_framework.permissions import BasePermission

from apps.tasks.models import Task


class IsUserAssociatedWithTask(BasePermission):
    """
    Permission to check if the user is associated with the task.
    """

    message = "You are not associated with this task."

    def has_permission(self, request, view):
        task = view.get_task()
        return request.user in [task.client, task.freelancer]


class IsTaskCompleted(BasePermission):
    """
    Permission to check if the task is completed.
    """

    message = "This task is not completed."

    def has_permission(self, request, view):
        task = view.get_task()
        return task.status == Task.TaskStatus.COMPLETED


class IsFreelancerAssignedToTask(BasePermission):
    """
    Permission to check if a freelancer is assigned to the task.
    """

    message = "No freelancer is assigned to this task."

    def has_permission(self, request, view):
        task = view.get_task()
        return task.freelancer is not None


class IsReviewCreator(BasePermission):
    """
    Permission to check if the user is the creator of the review.
    """

    message = "You are not the creator of this review."

    def has_object_permission(self, request, view, review):
        return review.reviewer == request.user

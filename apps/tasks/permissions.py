from rest_framework.permissions import BasePermission

from .models import Task


class IsTaskOpen(BasePermission):
    def has_object_permission(self, request, view, task):
        return task.status == Task.TaskStatus.OPEN


class IsTaskOwner(BasePermission):
    def has_object_permission(self, request, view, task):
        return task.client == request.user


class IsProposalOwner(BasePermission):
    def has_object_permission(self, request, view, proposal):
        return proposal.freelancer == request.user


class IsProposalTaskOwner(BasePermission):
    def has_object_permission(self, request, view, proposal):
        return proposal.task.client == request.user

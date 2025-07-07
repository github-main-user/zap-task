from rest_framework.permissions import BasePermission

from apps.tasks.models import Task

from .models import Proposal


class IsProposalPending(BasePermission):
    def has_object_permission(self, request, view, proposal):
        return proposal.status == Proposal.ProposalStatus.PENDING


class IsProposalOwner(BasePermission):
    def has_object_permission(self, request, view, proposal):
        return proposal.freelancer == request.user


class IsTaskOwner(BasePermission):
    def has_object_permission(self, request, view, proposal):
        task = view.get_task()
        return task.client == request.user


class IsTaskOpen(BasePermission):
    def has_permission(self, request, view):
        task = view.get_task()
        return task.status == Task.TaskStatus.OPEN

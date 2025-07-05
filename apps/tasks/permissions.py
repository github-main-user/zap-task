from rest_framework.permissions import BasePermission

from .models import Proposal, Task

# Task


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


# Proposal


class IsProposalPending(BasePermission):
    def has_object_permission(self, request, view, proposal):
        return proposal.status == Proposal.ProposalStatus.PENDING


class IsProposalOwner(BasePermission):
    def has_object_permission(self, request, view, proposal):
        return proposal.freelancer == request.user


class IsProposalTaskOwner(BasePermission):
    def has_object_permission(self, request, view, proposal):
        return proposal.task.client == request.user

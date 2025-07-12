from rest_framework.permissions import BasePermission

from apps.tasks.models import Task

from .models import Proposal


class IsProposalPending(BasePermission):
    """Permission to check if a proposal is pending."""

    message = "This action can only be performed on pending proposals."

    def has_object_permission(self, request, view, proposal):
        return proposal.status == Proposal.ProposalStatus.PENDING


class IsFreelancerOfProposal(BasePermission):
    """Permission to check if the user is the freelancer of the proposal."""

    message = "You are not the freelancer of this proposal."

    def has_object_permission(self, request, view, proposal):
        return proposal.freelancer == request.user


class IsClientOfTask(BasePermission):
    """Permission to check if the user is the client of the task."""

    message = "You are not the client of this task."

    def has_object_permission(self, request, view, proposal):
        task = view.get_task()
        return task.client == request.user


class IsTaskOpen(BasePermission):
    """Permission to check if the task is open."""

    message = "This task is not open for proposals."

    def has_permission(self, request, view):
        task = view.get_task()
        return task.status == Task.TaskStatus.OPEN

from rest_framework.permissions import BasePermission

from .models import Proposal


class IsProposalPending(BasePermission):
    def has_object_permission(self, request, view, proposal):
        return proposal.status == Proposal.ProposalStatus.PENDING


class IsProposalOwner(BasePermission):
    def has_object_permission(self, request, view, proposal):
        return proposal.freelancer == request.user


class IsProposalTaskOwner(BasePermission):
    def has_object_permission(self, request, view, proposal):
        return proposal.task.client == request.user

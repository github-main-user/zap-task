from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.tasks.permissions import IsTaskOpen
from apps.users.permissions import IsFreelancer

from .models import Proposal, Task
from .permissions import (
    IsClientOfTask,
    IsFreelancerOfProposal,
    IsProposalPending,
)
from .serializers import ProposalSerializer


@extend_schema(tags=["Proposals"])
class ProposalViewSet(viewsets.ModelViewSet):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "freelancer"]
    search_fields = ["message"]
    ordering_fields = ["created_at", "updated_at"]

    @extend_schema(
        summary="List proposals for a specific task",
        description="Retrieves a list of proposals associated with a specific task. "
        "Accessible by authenticated users.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a proposal for a specific task",
        description="Retrieves the details of a specific proposal associated with a "
        "task. Accessible by the client of the task or "
        "the freelancer who created the proposal.",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new proposal for a task",
        description="Allows a freelancer to create a new proposal for an open task.",
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Update a proposal",
        description="Updates an existing proposal. Only the freelancer who created "
        "the proposal can update it, and only if the proposal is pending.",
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update a proposal",
        description="Partially updates an existing proposal. Only the freelancer who "
        "created the proposal can update it, and only if the proposal is pending.",
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete a proposal",
        description="Deletes a proposal. Only the freelancer who created the proposal "
        "can delete it, and only if the proposal is pending.",
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_task(self):
        if not hasattr(self, "_task"):
            self._task = get_object_or_404(Task, pk=self.kwargs.get("task_pk"))
        return self._task

    def get_queryset(self):
        return self.queryset.filter(task=self.get_task())

    def get_permissions(self):
        permissions = [IsAuthenticated]
        # default actions
        if self.action == "create":
            permissions += [IsFreelancer, IsTaskOpen]
        elif self.action == "retrieve":
            permissions += [IsClientOfTask | IsFreelancerOfProposal]
        elif self.action in ["update", "partial_update", "destroy"]:
            permissions += [IsProposalPending, IsFreelancerOfProposal]
        # custom actions
        elif self.action in ["accept", "reject"]:
            permissions += [IsProposalPending, IsClientOfTask]

        return [permission() for permission in permissions]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["task"] = self.get_task()
        context["freelancer"] = self.request.user
        return context

    @extend_schema(
        summary="Accept a proposal",
        description="Allows the client of the task to accept a pending proposal. "
        "This will assign the freelancer of the proposal to the task, and reject all "
        "other proposals.",
        request=None,
    )
    @action(detail=True, methods=["post"])
    def accept(self, *args, **kwargs):
        proposal = self.get_object()
        proposal.accept()
        return Response(self.get_serializer(proposal).data)

    @extend_schema(
        summary="Reject a proposal",
        description="Allows the client of the task to reject a pending proposal.",
        request=None,
    )
    @action(detail=True, methods=["post"])
    def reject(self, *args, **kwargs):
        proposal = self.get_object()
        proposal.reject()
        return Response(self.get_serializer(proposal).data)

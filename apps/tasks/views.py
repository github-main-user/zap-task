from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.permissions import IsClient, IsFreelancer

from .models import Proposal, Task
from .permissions import (
    IsProposalOwner,
    IsProposalPending,
    IsProposalTaskOwner,
    IsTaskOpen,
    IsTaskOwner,
)
from .serializers import ProposalSerializer, TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    lookup_field = "id"

    def get_permissions(self):
        permissions = [IsAuthenticated]
        if self.action in ["create"]:
            permissions += [IsClient]
        elif self.action in ["update", "partial_update", "destroy"]:
            permissions += [IsTaskOpen, IsTaskOwner]
        return [permission() for permission in permissions]

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)


class ProposalViewSet(viewsets.ModelViewSet):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer

    def get_queryset(self):
        task_id = self.kwargs.get("task_id")
        return self.queryset.filter(task__id=task_id)

    def get_permissions(self):
        permissions = [IsAuthenticated]
        if self.action == "create":
            permissions += [IsFreelancer]
        elif self.action == "retrieve":
            permissions += [IsProposalTaskOwner | IsProposalOwner]
        elif self.action in ["update", "partial_update", "destroy"]:
            permissions += [IsProposalPending, IsProposalOwner]
        elif self.action in ["accept", "reject"]:
            permissions += [IsProposalPending, IsProposalTaskOwner]
        return [permission() for permission in permissions]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        task = get_object_or_404(Task, id=self.kwargs.get("task_id"))
        context |= {"task": task, "freelancer": self.request.user}
        return context

    @action(detail=True, methods=["post"])
    def accept(self, request, task_id=None, pk=None):
        proposal = self.get_object()
        proposal.accept()
        return Response(self.get_serializer(proposal).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, task_id=None, pk=None):
        proposal = self.get_object()
        proposal.reject()
        return Response(self.get_serializer(proposal).data)

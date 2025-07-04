from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

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
        return Proposal.objects.filter(task__id=task_id)

    def get_permissions(self):
        permissions = [IsAuthenticated]
        if self.action in ["create"]:
            permissions += [IsFreelancer]
        elif self.action in ["retrieve"]:
            permissions += [IsProposalTaskOwner | IsProposalOwner]
        elif self.action in ["update", "partial_update", "destroy"]:
            permissions += [IsProposalPending, IsProposalOwner]
        return [permission() for permission in permissions]

    def perform_create(self, serializer):
        task = get_object_or_404(Task, id=self.kwargs.get("task_id"))
        serializer.save(task=task, freelancer=self.request.user)

from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.tasks.permissions import IsTaskOpen
from apps.users.permissions import IsFreelancer

from .models import Proposal, Task
from .permissions import (
    IsProposalOwner,
    IsProposalPending,
    IsTaskOwner,
)
from .serializers import ProposalSerializer


class ProposalViewSet(viewsets.ModelViewSet):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer

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
            permissions += [IsTaskOwner | IsProposalOwner]
        elif self.action in ["update", "partial_update", "destroy"]:
            permissions += [IsProposalPending, IsProposalOwner]
        # custom actions
        elif self.action in ["accept", "reject"]:
            permissions += [IsProposalPending, IsTaskOwner]

        return [permission() for permission in permissions]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["task"] = self.get_task()
        context["freelancer"] = self.request.user
        return context

    @action(detail=True, methods=["post"])
    def accept(self, *args, **kwargs):
        proposal = self.get_object()
        proposal.accept()
        return Response(self.get_serializer(proposal).data)

    @action(detail=True, methods=["post"])
    def reject(self, *args, **kwargs):
        proposal = self.get_object()
        proposal.reject()
        return Response(self.get_serializer(proposal).data)

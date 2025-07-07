from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.permissions import IsFreelancer

from .models import Proposal, Task
from .permissions import (
    IsProposalOwner,
    IsProposalPending,
    IsProposalTaskOwner,
)
from .serializers import ProposalSerializer


class ProposalViewSet(viewsets.ModelViewSet):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer

    def get_queryset(self):
        task_pk = self.kwargs.get("task_pk")
        return self.queryset.filter(task__pk=task_pk)

    def get_permissions(self):
        permissions = [IsAuthenticated]
        # default actions
        if self.action == "create":
            permissions += [IsFreelancer]
        elif self.action == "retrieve":
            permissions += [IsProposalTaskOwner | IsProposalOwner]
        elif self.action in ["update", "partial_update", "destroy"]:
            permissions += [IsProposalPending, IsProposalOwner]
        # custom actions
        elif self.action in ["accept", "reject"]:
            permissions += [IsProposalPending, IsProposalTaskOwner]

        return [permission() for permission in permissions]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        task = get_object_or_404(Task, pk=self.kwargs.get("task_pk"))
        context |= {"task": task, "freelancer": self.request.user}
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

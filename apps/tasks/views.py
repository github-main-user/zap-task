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
    IsTaskFreelancer,
    IsTaskInProgress,
    IsTaskOpen,
    IsTaskOwner,
    IsTaskPendingReview,
)
from .serializers import ProposalSerializer, TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_permissions(self):
        permissions = [IsAuthenticated]
        # default actions
        if self.action == "create":
            permissions += [IsClient]
        elif self.action in ["update", "partial_update", "destroy"]:
            permissions += [IsTaskOpen, IsTaskOwner]
        # custom actions
        elif self.action == "start":
            permissions += [IsTaskOpen, IsTaskFreelancer]
        elif self.action == "submit":
            permissions += [IsTaskInProgress, IsTaskFreelancer]
        elif self.action in ["approve_submission", "reject_submission"]:
            permissions += [IsTaskPendingReview, IsTaskOwner]
        elif self.action == "cancel":
            permissions += [IsTaskOpen, IsTaskFreelancer | IsTaskOwner]

        return [permission() for permission in permissions]

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        task = self.get_object()
        task.start()
        return Response(self.get_serializer(task).data)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        task = self.get_object()
        task.begin_review()
        return Response(self.get_serializer(task).data)

    @action(detail=True, methods=["post"])
    def approve_submission(self, request, pk=None):
        task = self.get_object()
        task.complete()
        return Response(self.get_serializer(task).data)

    @action(detail=True, methods=["post"])
    def reject_submission(self, request, pk=None):
        task = self.get_object()
        task.start()
        return Response(self.get_serializer(task).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        task = self.get_object()
        task.cancel()
        return Response(self.get_serializer(task).data)


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
    def accept(self, request, task_pk=None, pk=None):
        proposal = self.get_object()
        proposal.accept()
        return Response(self.get_serializer(proposal).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, task_pk=None, pk=None):
        proposal = self.get_object()
        proposal.reject()
        return Response(self.get_serializer(proposal).data)

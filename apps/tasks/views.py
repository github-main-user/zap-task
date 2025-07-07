from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.permissions import IsClient

from .models import Task
from .permissions import (
    IsTaskFreelancer,
    IsTaskInProgress,
    IsTaskOpen,
    IsTaskOwner,
    IsTaskPendingReview,
)
from .serializers import TaskSerializer


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
    def start(self, *args, **kwargs):
        task = self.get_object()
        task.start()
        return Response(self.get_serializer(task).data)

    @action(detail=True, methods=["post"])
    def submit(self, *args, **kwargs):
        task = self.get_object()
        task.begin_review()
        return Response(self.get_serializer(task).data)

    @action(detail=True, methods=["post"])
    def approve_submission(self, *args, **kwargs):
        task = self.get_object()
        task.complete()
        return Response(self.get_serializer(task).data)

    @action(detail=True, methods=["post"])
    def reject_submission(self, *args, **kwargs):
        task = self.get_object()
        task.start()
        return Response(self.get_serializer(task).data)

    @action(detail=True, methods=["post"])
    def cancel(self, *args, **kwargs):
        task = self.get_object()
        task.cancel()
        return Response(self.get_serializer(task).data)

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.users.permissions import IsClient

from .models import Task
from .permissions import (
    IsClientOfTask,
    IsFreelancerOfTask,
    IsTaskInProgress,
    IsTaskOpen,
    IsTaskPendingReview,
)
from .serializers import TaskSerializer


@extend_schema(tags=["Tasks"])
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "client", "freelancer"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "price", "deadline"]

    @extend_schema(
        summary="List all tasks",
        description="Retrieves a list of all tasks. Accessible by all users.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a task",
        description="Retrieves the details of a specific task. Accessible by "
        "authenticated users.",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new task",
        description="Creates a new task. Only clients can create tasks.",
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Update a task",
        description="Updates an existing task. Only the client who created the task "
        "can update it, and only if the task is open.",
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update a task",
        description="Partially updates an existing task. Only the client who created "
        "the task can update it, and only if the task is open.",
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete a task",
        description="Deletes a task. Only the client who created the task can delete "
        "it, and only if the task is open.",
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_permissions(self):
        permissions = [IsAuthenticated]
        # default actions
        if self.action == "list":
            permissions = [AllowAny]
        if self.action == "create":
            permissions += [IsClient]
        elif self.action in ["update", "partial_update", "destroy"]:
            permissions += [IsTaskOpen, IsClientOfTask]
        # custom actions
        elif self.action == "start":
            permissions += [IsTaskOpen, IsFreelancerOfTask]
        elif self.action == "submit":
            permissions += [IsTaskInProgress, IsFreelancerOfTask]
        elif self.action in ["approve_submission", "reject_submission"]:
            permissions += [IsTaskPendingReview, IsClientOfTask]
        elif self.action == "cancel":
            permissions += [IsTaskOpen, IsFreelancerOfTask | IsClientOfTask]

        return [permission() for permission in permissions]

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

    @extend_schema(
        summary="Start a task",
        description="Allows a freelancer to start a task. Only accessible if the task "
        "is open and the user is the assigned freelancer.",
        request=None,
    )
    @action(detail=True, methods=["post"])
    def start(self, *args, **kwargs):
        task = self.get_object()
        task.start()
        return Response(self.get_serializer(task).data)

    @extend_schema(
        summary="Submit a task",
        description="Allows a freelancer to submit a task for review. Only accessible "
        "if the task is in progress and the user is the assigned freelancer.",
        request=None,
    )
    @action(detail=True, methods=["post"])
    def submit(self, *args, **kwargs):
        task = self.get_object()
        task.begin_review()
        return Response(self.get_serializer(task).data)

    @extend_schema(
        summary="Approve a task submission",
        description="Allows a client to approve a task submission. Only accessible if "
        "the task is pending review and the user is the client of the task.",
        request=None,
    )
    @action(detail=True, methods=["post"])
    def approve_submission(self, *args, **kwargs):
        task = self.get_object()
        task.complete()
        return Response(self.get_serializer(task).data)

    @extend_schema(
        summary="Reject a task submission",
        description="Allows a client to reject a task submission, returning it to "
        "'in progress' status. Only accessible if the task is pending review and the "
        "user is the client of the task.",
        request=None,
    )
    @action(detail=True, methods=["post"])
    def reject_submission(self, *args, **kwargs):
        task = self.get_object()
        task.start()
        return Response(self.get_serializer(task).data)

    @extend_schema(
        summary="Cancel a task",
        description="Allows a client or freelancer to cancel an open task. Only "
        "accessible if the task is open and the user is either the client or the "
        "assigned freelancer.",
        request=None,
    )
    @action(detail=True, methods=["post"])
    def cancel(self, *args, **kwargs):
        task = self.get_object()
        task.cancel()
        return Response(self.get_serializer(task).data)

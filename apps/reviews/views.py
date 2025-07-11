from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.tasks.models import Task

from .models import Review
from .permissions import (
    IsFreelancerAssignedToTask,
    IsTaskCompleted,
    IsUserAssociatedWithTask,
)
from .serializers import ReviewSerializer


from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.tasks.models import Task

from .models import Review
from .permissions import (
    IsFreelancerAssignedToTask,
    IsTaskCompleted,
    IsUserAssociatedWithTask,
)
from .serializers import ReviewSerializer

import logging

logger = logging.getLogger(__name__)


@extend_schema(tags=["Reviews"])
class ReviewViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
): 
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["reviewer", "recipient"]
    search_fields = ["comment"]
    ordering_fields = ["created_at", "rating"]

    @extend_schema(
        summary="List reviews for a specific task",
        description="Retrieves a list of reviews associated with a specific task. "
        "Accessible by authenticated users.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a review for a specific task",
        description="Retrieves the details of a specific review associated with a "
        "task. Accessible by authenticated users.",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Create a review for a task",
        description="Allows an authenticated user to create a review for a completed "
        "task. Only the client or freelancer associated with the task can create a "
        "review.",
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def get_task(self):
        if not hasattr(self, "_task"):
            self._task = get_object_or_404(Task, pk=self.kwargs.get("task_pk"))
        return self._task

    def get_queryset(self):
        return self.queryset.filter(task=self.get_task())

    def get_permissions(self):
        permissions = [IsAuthenticated]
        if self.action == "create":
            permissions += [
                IsUserAssociatedWithTask,
                IsTaskCompleted,
                IsFreelancerAssignedToTask,
            ]

        return [permission() for permission in permissions]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["task"] = self.get_task()
        return context

    def perform_create(self, serializer):
        task = self.get_task()
        reviewer = self.request.user
        recipient = task.freelancer if reviewer == task.client else task.client
        serializer.save(reviewer=reviewer, recipient=recipient, task=task)
        logger.info(
            f"Review for task '{task.title}' created by {reviewer.email} for "
            f"{recipient.email}."
        )

from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.tasks.models import Task

from .models import Review
from .permissions import (
    IsFreelancerAssignedToTask,
    IsPartOfTask,
    IsReviewOwner,
    IsTaskCompleted,
)
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_task(self):
        if not hasattr(self, "_task"):
            self._task = get_object_or_404(Task, pk=self.kwargs.get("task_pk"))
        return self._task

    def get_queryset(self):
        task_pk = self.kwargs.get("task_pk")
        return self.queryset.filter(task__pk=task_pk)

    def get_permissions(self):
        permissions = [IsAuthenticated]
        if self.action == "create":
            permissions += [IsPartOfTask, IsTaskCompleted, IsFreelancerAssignedToTask]
        if self.action in ["update", "partial_update", "destroy"]:
            permissions += [IsReviewOwner]

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

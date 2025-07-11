import logging

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import filters, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.core.tasks import send_email_notification
from apps.payments.services import StripeService
from apps.users.permissions import IsClient

from . import services
from .models import Task
from .permissions import (
    IsClientOfTask,
    IsFreelancerAssingedToTask,
    IsFreelancerOfTask,
    IsTaskInProgress,
    IsTaskOpen,
    IsTaskPaid,
    IsTaskPendingReview,
)
from .serializers import TaskSerializer

logger = logging.getLogger(__name__)


@extend_schema(tags=["Tasks"])
@extend_schema_view(
    list=extend_schema(
        summary="List all tasks",
        description="Retrieves a list of all tasks. Accessible by all users.",
    ),
    retrieve=extend_schema(
        summary="Retrieve a task",
        description="Retrieves the details of a specific task. Accessible by "
        "authenticated users.",
    ),
    create=extend_schema(
        summary="Create a new task",
        description="Creates a new task. Only clients can create tasks.",
    ),
    update=extend_schema(
        summary="Update a task",
        description="Updates an existing task. Only the client who created the task "
        "can update it, and only if the task is open.",
    ),
    partial_update=extend_schema(
        summary="Partially update a task",
        description="Partially updates an existing task. Only the client who created "
        "the task can update it, and only if the task is open.",
    ),
    destroy=extend_schema(
        summary="Delete a task",
        description="Deletes a task. Only the client who created the task can delete "
        "it, and only if the task is open.",
    ),
)
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

    def get_permissions(self):
        permissions = [IsAuthenticated]
        # default actions
        if self.action == "list":
            permissions = [AllowAny]
        elif self.action == "create":
            permissions += [IsClient]
        elif self.action in ["update", "partial_update", "destroy"]:
            permissions += [IsTaskOpen, IsClientOfTask]
        # custom actions
        elif self.action == "start":
            permissions += [IsTaskPaid, IsFreelancerOfTask]
        elif self.action == "submit":
            permissions += [IsTaskInProgress, IsFreelancerOfTask]
        elif self.action in ["approve_submission", "reject_submission"]:
            permissions += [IsTaskPendingReview, IsClientOfTask]
        elif self.action == "cancel":
            permissions += [IsTaskOpen, IsFreelancerOfTask | IsClientOfTask]
        elif self.action == "pay":
            permissions += [IsTaskOpen, IsFreelancerAssingedToTask, IsClientOfTask]

        return [permission() for permission in permissions]

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)
        logger.info(
            f"Task '{serializer.instance.title}' created by user "
            f"{self.request.user.email}."
        )
        send_email_notification.delay(
            subject="Task Created",
            message=f"Task '{serializer.instance.title}' was created.",
            recipient_list=[self.request.user.email],
        )

    @extend_schema(
        summary="Start a task",
        description="Allows a freelancer to start a task. Only accessible if the task "
        "is paid by client and the user is the assigned freelancer of the task.",
        request=None,
    )
    @action(detail=True, methods=["post"])
    def start(self, *args, **kwargs):
        task = self.get_object()
        services.start_task(task)
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
        services.submit_task(task)
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
        services.approve_task_submission(task)
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
        services.reject_task_submission(task)
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
        services.cancel_task(task, self.request.user)
        return Response(self.get_serializer(task).data)

    @extend_schema(
        summary="Create checkout session",
        description="Creates Stripe checkout session to pay the task. Only task client "
        "can create.",
        responses={
            200: OpenApiResponse(
                description="Checkout session created",
                response=inline_serializer(
                    name="CheckoutSession",
                    fields={"checkout_url": serializers.URLField()},
                ),
            ),
            500: OpenApiResponse(description="Failed to create checkout url"),
        },
    )
    @action(detail=True, methods=["post"])
    def pay(self, *args, **kwargs):
        task = self.get_object()
        stripe_service = StripeService()
        checkout_session_url = stripe_service.create_checkout_session(task)
        if checkout_session_url is None:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"checkout_url": checkout_session_url})

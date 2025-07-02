from django.contrib.auth import get_user_model
from django.db import models

from apps.core.models import TimeStampModel

User = get_user_model()


class Task(TimeStampModel):
    class TaskStatus(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"
        CANCELED = "canceled", "Canceled"

    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    deadline = models.DateTimeField()
    status = models.CharField(
        max_length=15, choices=TaskStatus.choices, default=TaskStatus.OPEN
    )
    client = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="client_tasks"
    )
    freelancer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="freelancer_tasks",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["deadline"]),
        ]

    def __str__(self) -> str:
        return f"Task #{self.pk} '{self.title}' [{self.status}]"


class Proposal(TimeStampModel):
    class ProposalStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="proposals")
    message = models.TextField()
    price_offer = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    freelancer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="proposals"
    )
    status = models.CharField(
        max_length=8, choices=ProposalStatus.choices, default=ProposalStatus.PENDING
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=("task", "freelancer"), name="unique_task_per_freelancer"
            )
        ]
        indexes = [models.Index(fields=["status"])]

    def __str__(self):
        return (
            f"Proposal #{self.pk} for '{self.task.title}' "
            f"by {self.freelancer.username} [{self.status}]"
        )

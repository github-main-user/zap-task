from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

from apps.core.models import TimeStampModel

User = get_user_model()


class Task(TimeStampModel):
    class TaskStatus(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In progress"
        PENDING_REVIEW = "pending_review", "Pending review"
        COMPLETED = "completed", "Completed"
        CANCELED = "canceled", "Canceled"

    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
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

    def start(self):
        self.status = self.TaskStatus.IN_PROGRESS
        self.save()

    def begin_review(self):
        self.status = self.TaskStatus.PENDING_REVIEW
        self.save()

    def complete(self):
        self.status = self.TaskStatus.COMPLETED
        self.save()

    def cancel(self):
        self.status = self.TaskStatus.CANCELED
        self.save()

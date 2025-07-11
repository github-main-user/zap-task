from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django_fsm import FSMField, transition

from apps.core.models import TimeStampModel

User = get_user_model()


class Task(TimeStampModel):
    class TaskStatus(models.TextChoices):
        OPEN = "open", "Open"
        PAID = "paid", "Paid"
        IN_PROGRESS = "in_progress", "In progress"
        PENDING_REVIEW = "pending_review", "Pending review"
        COMPLETED = "completed", "Completed"
        CANCELED = "canceled", "Canceled"
        EXPIRED = "expired", "Expired"

    title = models.CharField(max_length=200, help_text="Title of the task.")
    description = models.TextField(help_text="Detailed description of the task.")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Price for the task.",
    )
    deadline = models.DateTimeField(help_text="Deadline for the task.")
    status = FSMField(
        max_length=15,
        choices=TaskStatus.choices,
        default=TaskStatus.OPEN,
        help_text="Current status of the task.",
    )
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="client_tasks",
        help_text="User who created the task.",
    )
    freelancer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="freelancer_tasks",
        null=True,
        blank=True,
        help_text="User who is assigned to the task.",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["deadline"]),
        ]

    def __str__(self) -> str:
        return f"Task #{self.pk} '{self.title}' [{self.status}]"

    def has_freelancer(self) -> bool:
        return self.freelancer is not None

    @transition(field=status, source=TaskStatus.OPEN, target=TaskStatus.PAID, conditions=[has_freelancer])
    def pay(self) -> None: ...

    @transition(
        field=status,
        source=TaskStatus.PAID,
        target=TaskStatus.IN_PROGRESS,
        conditions=[has_freelancer],
    )
    def start(self) -> None: ...

    @transition(
        field=status, source=TaskStatus.IN_PROGRESS, target=TaskStatus.PENDING_REVIEW
    )
    def begin_review(self) -> None: ...

    @transition(
        field=status, source=TaskStatus.PENDING_REVIEW, target=TaskStatus.COMPLETED
    )
    def complete(self) -> None: ...

    @transition(
        field=status, source=TaskStatus.PENDING_REVIEW, target=TaskStatus.IN_PROGRESS
    )
    def reject(self) -> None: ...

    @transition(field=status, source=TaskStatus.OPEN, target=TaskStatus.CANCELED)
    def cancel(self) -> None: ...

    @transition(
        field=status,
        source=[TaskStatus.OPEN, TaskStatus.PAID, TaskStatus.IN_PROGRESS],
        target=TaskStatus.EXPIRED,
    )
    def expire(self) -> None: ...

from django.contrib.auth import get_user_model
from django.db import models

from apps.core.models import TimeStampModel
from apps.tasks.models import Task

User = get_user_model()


class Payment(TimeStampModel):
    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="payments",
        help_text="The task associated with this payment.",
    )
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payments",
        help_text="The client making the payment.",
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="The amount of the payment."
    )
    status = models.CharField(
        max_length=10,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        help_text="The status of the payment.",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Payment for Task #{self.task.pk} - {self.amount} ({self.status})"

from django.contrib.auth import get_user_model
from django.db import models
from rest_framework.fields import MaxValueValidator, MinValueValidator

from apps.tasks.models import Task

User = get_user_model()


class Review(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="reviews",
        help_text="Task being reviewed.",
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="given_reviews",
        help_text="User who wrote the review.",
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_reviews",
        help_text="User who received the review.",
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5.",
    )
    comment = models.TextField(blank=True, help_text="Review comment.")
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Date and time when the review was created."
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=("task", "reviewer"), name="unique_reviewer_per_task"
            )
        ]

    def __str__(self) -> str:
        return f"Review #{self.pk} from {self.reviewer.pk} to {self.recipient.pk}"

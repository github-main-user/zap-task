from django.contrib.auth import get_user_model
from django.db import models
from django_fsm import FSMField, transition

from apps.core.models import TimeStampModel
from apps.tasks.models import Task

User = get_user_model()


class Proposal(TimeStampModel):
    class ProposalStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="proposals",
        help_text="Task for which the proposal is made.",
    )
    message = models.TextField(blank=True, help_text="Proposal message.")
    freelancer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="proposals",
        help_text="Freelancer who made the proposal.",
    )
    status = FSMField(
        max_length=8,
        choices=ProposalStatus.choices,
        default=ProposalStatus.PENDING,
        help_text="Current status of the proposal.",
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=("task", "freelancer"), name="unique_task_per_freelancer"
            )
        ]
        indexes = [models.Index(fields=["status"])]

    def __str__(self) -> str:
        return (
            f"Proposal #{self.pk} for '{self.task.title}' "
            f"by {self.freelancer.username} [{self.status}]"
        )

    def can_accept(self) -> bool:
        return self.task.status == Task.TaskStatus.OPEN

    @transition(
        field=status,
        source=ProposalStatus.PENDING,
        target=ProposalStatus.ACCEPTED,
        conditions=[can_accept],
    )
    def accept(self) -> None:
        self.task.freelancer = self.freelancer
        self.task.save()
        Proposal.objects.filter(task=self.task).exclude(pk=self.pk).update(
            status=self.ProposalStatus.REJECTED
        )

    @transition(
        field=status,
        source=ProposalStatus.PENDING,
        target=ProposalStatus.REJECTED,
    )
    def reject(self) -> None: ...

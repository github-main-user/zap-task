from apps.core.tasks import send_email_task

from .models import Proposal


def accept_proposal(proposal: Proposal) -> None:
    """
    Accepts a proposal, updates the associated task, rejects other proposals,
    and sends email notifications.
    """
    proposal.accept()
    proposal.save()

    # Send email to the freelancer whose proposal was accepted
    send_email_task.delay(
        subject="Proposal Accepted!",
        message=f"Your proposal for task '{proposal.task.title}' has been accepted!",
        recipient_list=[proposal.freelancer.email],
    )

    # Send email to other freelancers whose proposals were rejected
    rejected_proposals = Proposal.objects.filter(task=proposal.task).exclude(
        pk=proposal.pk
    )
    for rejected_proposal in rejected_proposals:
        send_email_task.delay(
            subject="Proposal Rejected",
            message=(
                f"Your proposal for task '{rejected_proposal.task.title}' was rejected."
            ),
            recipient_list=[rejected_proposal.freelancer.email],
        )


def reject_proposal(proposal: Proposal) -> None:
    """
    Rejects a proposal and sends an email notification.
    """
    proposal.reject()
    proposal.save()

    send_email_task.delay(
        subject="Proposal Rejected",
        message=f"Your proposal for task '{proposal.task.title}' was rejected.",
        recipient_list=[proposal.freelancer.email],
    )

import logging

from apps.core.tasks import send_email_notification

from .models import Proposal

logger = logging.getLogger(__name__)


def accept_proposal(proposal: Proposal) -> None:
    """
    Accepts a proposal, updates the associated task, rejects other proposals,
    and sends email notifications.
    """
    proposal.task.freelancer = proposal.freelancer
    proposal.task.save()
    proposal.accept()
    proposal.save()

    logger.info(
        f"Proposal for task '{proposal.task.title}' from {proposal.freelancer.email} "
        f"accepted by {proposal.task.client.email}."
    )

    # Send email to the freelancer whose proposal was accepted
    send_email_notification.delay(
        subject="Proposal Accepted!",
        message=f"Your proposal for task '{proposal.task.title}' has been accepted!",
        recipient_list=[proposal.freelancer.email],
    )

    # Send email to other freelancers whose proposals were rejected
    proposals_to_reject = Proposal.objects.filter(task=proposal.task).exclude(
        pk=proposal.pk
    )
    proposals_to_reject.update(status=Proposal.ProposalStatus.REJECTED)
    for proposal in proposals_to_reject:
        logger.info(
            f"Proposal for task '{proposal.task.title}' "
            f"from {proposal.freelancer.email} "
            f"rejected by {proposal.task.client.email}."
        )
        send_email_notification.delay(
            subject="Proposal Rejected",
            message=(f"Your proposal for task '{proposal.task.title}' was rejected."),
            recipient_list=[proposal.freelancer.email],
        )


def reject_proposal(proposal: Proposal) -> None:
    """Rejects a proposal and sends an email notification."""

    proposal.reject()
    proposal.save()
    logger.info(
        f"Proposal for task '{proposal.task.title}' from {proposal.freelancer.email} "
        f"rejected by {proposal.task.client.email}."
    )

    send_email_notification.delay(
        subject="Proposal Rejected",
        message=f"Your proposal for task '{proposal.task.title}' was rejected.",
        recipient_list=[proposal.freelancer.email],
    )

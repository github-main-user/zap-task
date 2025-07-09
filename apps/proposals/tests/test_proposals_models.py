import pytest
from django.contrib.auth import get_user_model

from apps.core.exceptions import InvalidStateTransition
from apps.proposals.models import Proposal
from apps.tasks.models import Task

User = get_user_model()

# accept


@pytest.mark.django_db
def test_accept_proposal_successfully(task_obj, freelancer_user):
    proposal_to_accept = Proposal.objects.create(
        task=task_obj,
        freelancer=freelancer_user,
        status=Proposal.ProposalStatus.PENDING,
    )
    other_freelancer = User.objects.create_user(
        "other@freelancer.com", "password", role=User.UserRole.FREELANCER
    )
    other_proposal = Proposal.objects.create(
        task=task_obj,
        freelancer=other_freelancer,
        status=Proposal.ProposalStatus.PENDING,
    )

    proposal_to_accept.accept()

    proposal_to_accept.refresh_from_db()
    other_proposal.refresh_from_db()
    task_obj.refresh_from_db()
    assert proposal_to_accept.status == Proposal.ProposalStatus.ACCEPTED
    assert task_obj.freelancer == freelancer_user
    assert other_proposal.status == Proposal.ProposalStatus.REJECTED


def test_accept_proposal_with_invalid_status_raises_exception(proposal_obj):
    proposal_obj.status = Proposal.ProposalStatus.ACCEPTED
    proposal_obj.save()

    with pytest.raises(InvalidStateTransition):
        proposal_obj.accept()


def test_accept_proposal_for_non_open_task_raises_exception(proposal_obj):
    proposal_obj.task.status = Task.TaskStatus.IN_PROGRESS
    proposal_obj.task.save()

    with pytest.raises(InvalidStateTransition):
        proposal_obj.accept()


# reject


def test_reject_proposal_successfully(proposal_obj):
    assert proposal_obj.status == Proposal.ProposalStatus.PENDING
    proposal_obj.reject()
    assert proposal_obj.status == Proposal.ProposalStatus.REJECTED


def test_reject_proposal_with_invalid_status_raises_exception(proposal_obj):
    proposal_obj.status = Proposal.ProposalStatus.ACCEPTED
    proposal_obj.save()

    with pytest.raises(InvalidStateTransition):
        proposal_obj.reject()

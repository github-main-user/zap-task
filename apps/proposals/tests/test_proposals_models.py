import pytest
from django.contrib.auth import get_user_model
from django_fsm import TransitionNotAllowed

from apps.proposals.models import Proposal
from apps.tasks.models import Task

User = get_user_model()

# accept


@pytest.mark.django_db
def test_accept_proposal_successfully(proposal_obj):
    assert proposal_obj.status == Proposal.ProposalStatus.PENDING
    proposal_obj.accept()
    assert proposal_obj.status == Proposal.ProposalStatus.ACCEPTED


@pytest.mark.django_db
def test_accept_proposal_with_invalid_status_raises_exception(proposal_obj):
    proposal_obj.status = Proposal.ProposalStatus.ACCEPTED
    proposal_obj.save()

    with pytest.raises(TransitionNotAllowed):
        proposal_obj.accept()


@pytest.mark.django_db
def test_accept_proposal_for_non_open_task_raises_exception(proposal_obj):
    proposal_obj.task.status = Task.TaskStatus.IN_PROGRESS
    proposal_obj.task.save()

    with pytest.raises(TransitionNotAllowed):
        proposal_obj.accept()


# reject


@pytest.mark.django_db
def test_reject_proposal_successfully(proposal_obj):
    assert proposal_obj.status == Proposal.ProposalStatus.PENDING
    proposal_obj.reject()
    assert proposal_obj.status == Proposal.ProposalStatus.REJECTED


@pytest.mark.django_db
def test_reject_proposal_with_invalid_status_raises_exception(proposal_obj):
    proposal_obj.status = Proposal.ProposalStatus.ACCEPTED
    proposal_obj.save()

    with pytest.raises(TransitionNotAllowed):
        proposal_obj.reject()

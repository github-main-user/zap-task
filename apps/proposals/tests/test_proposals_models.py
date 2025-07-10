import pytest
from django.contrib.auth import get_user_model
from django_fsm import TransitionNotAllowed

from apps.proposals.models import Proposal
from apps.tasks.models import Task

User = get_user_model()

# accept


@pytest.mark.django_db
def test_accept_proposal_successfully(proposal_factory):
    proposal = proposal_factory()
    proposal.accept()
    assert proposal.status == Proposal.ProposalStatus.ACCEPTED


@pytest.mark.django_db
def test_accept_proposal_with_invalid_status_raises_exception(proposal_factory):
    proposal = proposal_factory(status=Proposal.ProposalStatus.ACCEPTED)

    with pytest.raises(TransitionNotAllowed):
        proposal.accept()


@pytest.mark.django_db
def test_accept_proposal_for_non_open_task_raises_exception(
    task_factory, proposal_factory
):
    task = task_factory(status=Task.TaskStatus.IN_PROGRESS)
    proposal = proposal_factory(task=task)

    with pytest.raises(TransitionNotAllowed):
        proposal.accept()


# reject


@pytest.mark.django_db
def test_reject_proposal_successfully(proposal_factory):
    proposal = proposal_factory()
    proposal.reject()
    assert proposal.status == Proposal.ProposalStatus.REJECTED


@pytest.mark.django_db
def test_reject_proposal_with_invalid_status_raises_exception(proposal_factory):
    proposal = proposal_factory(status=Proposal.ProposalStatus.ACCEPTED)

    with pytest.raises(TransitionNotAllowed):
        proposal.reject()

from functools import partial

import pytest
from django.contrib.auth import get_user_model

from apps.proposals.models import Proposal

User = get_user_model()


@pytest.fixture
def proposal_data():
    return {"message": "Test proposal Message"}


@pytest.fixture
def proposal_factory(db, freelancer_user, task_factory):
    task = task_factory()

    def _proposal_factory(**kwargs):
        defaults = {
            "task": task,
            "freelancer": freelancer_user,
            "message": "Test proposal message",
            "status": Proposal.ProposalStatus.PENDING,
        }
        defaults.update(kwargs)
        return Proposal.objects.create(**defaults)

    return _proposal_factory


@pytest.fixture
def proposals(db, freelancer_user, user_factory, proposal_factory):
    freelancer_factory = partial(user_factory, role=User.UserRole.FREELANCER)

    return (
        proposal_factory(
            freelancer=freelancer_user,
            message="Pending proposal 1",
        ),
        proposal_factory(
            freelancer=freelancer_factory(email="fr2@fr2.com"),
            message="Accepted proposal 1",
            status=Proposal.ProposalStatus.ACCEPTED,
        ),
        proposal_factory(
            freelancer=freelancer_factory(email="fr3@fr3.com"),
            message="Rejected proposal 1",
            status=Proposal.ProposalStatus.REJECTED,
        ),
        proposal_factory(
            freelancer=freelancer_factory(email="fr4@fr4.com"),
            message="Another pending proposal",
        ),
        proposal_factory(
            freelancer=freelancer_factory(email="fr5@fr5.com"),
            message="Yet another proposal",
        ),
    )

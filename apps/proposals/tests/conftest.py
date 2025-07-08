import pytest
from django.contrib.auth import get_user_model

from apps.proposals.models import Proposal

User = get_user_model()

# ==========
#  fixtures
# ==========


@pytest.fixture
def proposal_data():
    return {"message": "Proposal Message"}


@pytest.fixture
def proposal_obj(db, proposal_data, task_obj, freelancer_user):
    return Proposal.objects.create(
        **proposal_data, task=task_obj, freelancer=freelancer_user
    )


@pytest.fixture
def proposals(db, task_obj, freelancer_user):
    freelancer_user_2 = User.objects.create_user(
        email="freelancer2@example.com",
        password="password",
        role=User.UserRole.FREELANCER,
    )  # type: ignore
    freelancer_user_3 = User.objects.create_user(
        email="freelancer3@example.com",
        password="password",
        role=User.UserRole.FREELANCER,
    )  # type: ignore
    freelancer_user_4 = User.objects.create_user(
        email="freelancer4@example.com",
        password="password",
        role=User.UserRole.FREELANCER,
    )  # type: ignore
    freelancer_user_5 = User.objects.create_user(
        email="freelancer5@example.com",
        password="password",
        role=User.UserRole.FREELANCER,
    )  # type: ignore

    return (
        Proposal.objects.create(
            task=task_obj,
            freelancer=freelancer_user,
            message="Pending proposal 1",
            status=Proposal.ProposalStatus.PENDING,
        ),
        Proposal.objects.create(
            task=task_obj,
            freelancer=freelancer_user_2,
            message="Accepted proposal 1",
            status=Proposal.ProposalStatus.ACCEPTED,
        ),
        Proposal.objects.create(
            task=task_obj,
            freelancer=freelancer_user_3,
            message="Rejected proposal 1",
            status=Proposal.ProposalStatus.REJECTED,
        ),
        Proposal.objects.create(
            task=task_obj,
            freelancer=freelancer_user_4,
            message="Another pending proposal",
            status=Proposal.ProposalStatus.PENDING,
        ),
        Proposal.objects.create(
            task=task_obj,
            freelancer=freelancer_user_5,
            message="Yet another proposal",
            status=Proposal.ProposalStatus.PENDING,
        ),
    )

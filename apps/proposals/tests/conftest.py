import pytest
from django.contrib.auth import get_user_model

from apps.proposals.models import Proposal
from apps.tasks.models import Task

User = get_user_model()

# ==========
#  fixtures
# ==========


@pytest.fixture
def client_user(db):
    return User.objects.create_user(
        "owner@owner.com", "pass", role=User.UserRole.CLIENT
    )


@pytest.fixture
def freelancer_user(db):
    return User.objects.create_user(
        "foreign@foreign.com", "pass", role=User.UserRole.FREELANCER
    )


@pytest.fixture
def task_data():
    return {
        "title": "new_task",
        "description": "test",
        "price": 256.5,
        "deadline": "2099-12-31T23:59:59Z",
    }


@pytest.fixture
def proposal_data():
    return {"message": "Proposal Message"}


@pytest.fixture
def task_obj(db, task_data, client_user):
    return Task.objects.create(
        **task_data,
        status=Task.TaskStatus.OPEN,
        client=client_user,
    )


@pytest.fixture
def proposal_obj(db, proposal_data, task_obj, freelancer_user):
    return Proposal.objects.create(
        **proposal_data, task=task_obj, freelancer=freelancer_user
    )


@pytest.fixture
def tasks(db, task_data, client_user, freelancer_user):
    return (
        Task.objects.create(
            **task_data,
            status=Task.TaskStatus.OPEN,
            client=client_user,
        ),
        Task.objects.create(
            **task_data,
            status=Task.TaskStatus.COMPLETED,
            client=client_user,
            freelancer=freelancer_user,
        ),
    )

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.payments.models import Payment
from apps.proposals.models import Proposal
from apps.reviews.models import Review
from apps.tasks.models import Task

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


# users


@pytest.fixture
def user_factory(db):
    def _user_factory(**kwargs):
        defaults = {
            "email": "test@example.com",
            "password": "pass",
            "role": User.UserRole.CLIENT,
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)

    return _user_factory


@pytest.fixture
def client_user(db, user_factory):
    return user_factory(email="client@client.com")


@pytest.fixture
def freelancer_user(db, user_factory):
    return user_factory(
        email="freelancer@freelancer.com", role=User.UserRole.FREELANCER
    )


@pytest.fixture
def random_user(db, user_factory):
    return user_factory(email="random@random.com")


# tasks


@pytest.fixture
def task_data():
    return {
        "title": "Test Task",
        "description": "Description for test task",
        "price": 100.00,
        "deadline": "2099-12-31T23:59:59Z",
    }


@pytest.fixture
def task_factory(db, task_data, client_user):
    def _task_factory(**kwargs):
        defaults = task_data | {
            "client": client_user,
            "status": Task.TaskStatus.OPEN,
        }
        defaults.update(kwargs)
        return Task.objects.create(**defaults)

    return _task_factory


# proposals


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


# reviews
@pytest.fixture
def review_data():
    return {"rating": 4, "comment": "Good job, but not great🙄"}


@pytest.fixture
def review_factory(db, task_factory, client_user, freelancer_user):
    task = task_factory(freelancer=freelancer_user, status=Task.TaskStatus.COMPLETED)

    def _review_factory(**kwargs):
        defaults = {
            "task": task,
            "rating": 4,
            "comment": "Good job, but not great🙄",
            "reviewer": client_user,
            "recipient": freelancer_user,
        }
        defaults.update(kwargs)
        return Review.objects.create(**defaults)

    return _review_factory


# payments


@pytest.fixture
def payment_data():
    return {"amount": 100.00}


@pytest.fixture
def payment_factory(db, freelancer_user, task_factory):
    task = task_factory(freelancer=freelancer_user)

    def _payment_factory(**kwargs):
        defaults = {
            "task": task,
            "client": task.client,
            "amount": 100.00,
            "status": Payment.PaymentStatus.PENDING,
        }
        defaults.update(kwargs)
        return Payment.objects.create(**defaults)

    return _payment_factory

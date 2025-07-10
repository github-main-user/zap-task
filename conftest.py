import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

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

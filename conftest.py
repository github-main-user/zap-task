import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.tasks.models import Task

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


# Common fixtures
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
def random_user(db):
    return User.objects.create_user(
        "random@random.com", "pass", role=User.UserRole.CLIENT
    )


@pytest.fixture
def user_factory(db):
    def _user_factory(**kwargs):
        defaults = {
            "email": "test@example.com",
            "password": "password",
            "role": User.UserRole.CLIENT,
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)
    return _user_factory


@pytest.fixture
def task_data():
    return {
        "title": "new_task",
        "description": "test",
        "price": 256.5,
        "deadline": "2099-12-31T23:59:59Z",
    }


@pytest.fixture
def task_obj(db, task_data, client_user):
    return Task.objects.create(
        **task_data, status=Task.TaskStatus.OPEN, client=client_user
    )

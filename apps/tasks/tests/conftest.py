import pytest
from django.contrib.auth import get_user_model

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
def task_obj(db, task_data, client_user):
    return Task.objects.create(
        **task_data,
        status=Task.TaskStatus.OPEN,
        client=client_user,
    )


@pytest.fixture
def tasks(db, task_data, client_user, freelancer_user):
    return (
        Task.objects.create(
            status=Task.TaskStatus.OPEN,
            client=client_user,
            title="Open Task 1",
            description="Description for open task 1",
            price=100.00,
            deadline="2099-12-31T23:59:59Z",
        ),
        Task.objects.create(
            status=Task.TaskStatus.IN_PROGRESS,
            client=client_user,
            freelancer=freelancer_user,
            title="In Progress Task 1",
            description="Description for in progress task 1",
            price=200.00,
            deadline="2099-12-30T23:59:59Z",
        ),
        Task.objects.create(
            status=Task.TaskStatus.PENDING_REVIEW,
            client=client_user,
            freelancer=freelancer_user,
            title="Pending Review Task 1",
            description="Description for pending review task 1",
            price=300.00,
            deadline="2099-12-29T23:59:59Z",
        ),
        Task.objects.create(
            status=Task.TaskStatus.COMPLETED,
            client=client_user,
            freelancer=freelancer_user,
            title="Completed Task 1",
            description="Description for completed task 1",
            price=400.00,
            deadline="2099-12-28T23:59:59Z",
        ),
        Task.objects.create(
            status=Task.TaskStatus.CANCELED,
            client=client_user,
            title="Canceled Task 1",
            description="Description for canceled task 1",
            price=500.00,
            deadline="2099-12-27T23:59:59Z",
        ),
        Task.objects.create(
            status=Task.TaskStatus.OPEN,
            client=freelancer_user,  # Another client
            title="Open Task 2",
            description="Description for open task 2",
            price=50.00,
            deadline="2099-12-26T23:59:59Z",
        ),
        Task.objects.create(
            status=Task.TaskStatus.IN_PROGRESS,
            client=freelancer_user,
            freelancer=client_user,  # Another freelancer
            title="In Progress Task 2",
            description="Description for in progress task 2",
            price=150.00,
            deadline="2099-12-25T23:59:59Z",
        ),
    )

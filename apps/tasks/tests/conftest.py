import pytest
from django.contrib.auth import get_user_model

from apps.tasks.models import Task

User = get_user_model()


@pytest.fixture
def tasks(db, task_factory, client_user, freelancer_user, random_user):
    return (
        task_factory(
            title="Open Task 1",
            description="Description for open task 1",
            price=100.00,
            deadline="2099-12-31T23:59:59Z",
        ),
        task_factory(
            status=Task.TaskStatus.IN_PROGRESS,
            freelancer=freelancer_user,
            title="In Progress Task 1",
            description="Description for in progress task 1",
            price=200.00,
            deadline="2099-12-30T23:59:59Z",
        ),
        task_factory(
            status=Task.TaskStatus.PENDING_REVIEW,
            freelancer=freelancer_user,
            title="Pending Review Task 1",
            description="Description for pending review task 1",
            price=300.00,
            deadline="2099-12-29T23:59:59Z",
        ),
        task_factory(
            status=Task.TaskStatus.COMPLETED,
            freelancer=freelancer_user,
            title="Completed Task 1",
            description="Description for completed task 1",
            price=400.00,
            deadline="2099-12-28T23:59:59Z",
        ),
        task_factory(
            status=Task.TaskStatus.CANCELED,
            title="Canceled Task 1",
            description="Description for canceled task 1",
            price=500.00,
            deadline="2099-12-27T23:59:59Z",
        ),
        task_factory(
            client=random_user,  # Another client
            title="Open Task 2",
            description="Description for open task 2",
            price=50.00,
            deadline="2099-12-26T23:59:59Z",
        ),
        task_factory(
            status=Task.TaskStatus.IN_PROGRESS,
            client=random_user,
            freelancer=client_user,  # Another freelancer
            title="In Progress Task 2",
            description="Description for in progress task 2",
            price=150.00,
            deadline="2099-12-25T23:59:59Z",
        ),
    )

import pytest
from django.contrib.auth import get_user_model

from apps.reviews.models import Review
from apps.tasks.models import Task

User = get_user_model()

# ==========
#  fixtures
# ==========


@pytest.fixture
def review_data():
    return {"rating": 4, "comment": "Good job, but not great🙄"}


@pytest.fixture
def review_obj(db, review_data, task_obj, client_user, freelancer_user):
    task_obj.freelancer = freelancer_user
    task_obj.status = Task.TaskStatus.COMPLETED
    task_obj.save()
    return Review.objects.create(
        **review_data,
        task=task_obj,
        reviewer=client_user,
        recipient=freelancer_user,
    )


@pytest.fixture
def reviews(db, task_obj, client_user, freelancer_user):
    client_user_2 = User.objects.create_user(
        email="client2@example.com", password="pass", role=User.UserRole.CLIENT
    )
    freelancer_user_2 = User.objects.create_user(
        email="freelancer2@example.com", password="pass", role=User.UserRole.FREELANCER
    )

    task_obj.freelancer = freelancer_user
    task_obj.status = Task.TaskStatus.COMPLETED
    task_obj.save()

    task_obj_2 = Task.objects.create(
        title="Another task",
        description="Another description",
        price=100.00,
        deadline="2099-12-31T23:59:59Z",
        client=client_user_2,
        freelancer=freelancer_user_2,
        status=Task.TaskStatus.COMPLETED,
    )

    return (
        Review.objects.create(
            task=task_obj,
            reviewer=client_user,
            recipient=freelancer_user,
            rating=5,
            comment="Excellent work!",
        ),
        Review.objects.create(
            task=task_obj,
            reviewer=freelancer_user,
            recipient=client_user,
            rating=3,
            comment="Average performance.",
        ),
        Review.objects.create(
            task=task_obj_2,
            reviewer=client_user_2,
            recipient=freelancer_user_2,
            rating=4,
            comment="Good communication.",
        ),
        Review.objects.create(
            task=task_obj_2,
            reviewer=freelancer_user_2,
            recipient=client_user_2,
            rating=2,
            comment="Needs improvement.",
        ),
    )


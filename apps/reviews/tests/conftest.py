import pytest
from django.contrib.auth import get_user_model

from apps.tasks.models import Task

User = get_user_model()


@pytest.fixture
def reviews(
    db, client_user, freelancer_user, user_factory, task_factory, review_factory
):
    client_user2 = user_factory(email="cl1@cl1.com")
    freelancer_user2 = user_factory(email="fr2@fr2.com", role=User.UserRole.FREELANCER)

    task2 = task_factory(
        title="Another task",
        description="Another description",
        price=100.00,
        deadline="2099-12-31T23:59:59Z",
        client=client_user2,
        freelancer=freelancer_user2,
        status=Task.TaskStatus.COMPLETED,
    )

    return (
        review_factory(
            reviewer=client_user,
            recipient=freelancer_user,
            rating=5,
            comment="Excellent work!",
        ),
        review_factory(
            reviewer=freelancer_user,
            recipient=client_user,
            rating=3,
            comment="Average performance.",
        ),
        review_factory(
            task=task2,
            reviewer=client_user2,
            recipient=freelancer_user2,
            rating=4,
            comment="Good communication.",
        ),
        review_factory(
            task=task2,
            reviewer=freelancer_user2,
            recipient=client_user2,
            rating=2,
            comment="Needs improvement.",
        ),
    )

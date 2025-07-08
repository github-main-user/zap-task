import pytest
from django.contrib.auth import get_user_model

from apps.reviews.models import Review
from apps.tasks.models import Task

User = get_user_model()


@pytest.mark.django_db
def test_update_user_average_rating_on_review_creation():
    recipient = User.objects.create_user(
        email="recipient@test.com", password="password"
    )
    reviewer1 = User.objects.create_user(
        email="reviewer1@test.com", password="password"
    )
    reviewer2 = User.objects.create_user(
        email="reviewer2@test.com", password="password"
    )

    task1 = Task.objects.create(
        title="Test Task 1",
        description="Test Description 1",
        client=recipient,
        price=100,
        deadline="2025-12-31T23:59:59Z",
    )
    task2 = Task.objects.create(
        title="Test Task 2",
        description="Test Description 2",
        client=recipient,
        price=200,
        deadline="2025-12-31T23:59:59Z",
    )

    assert recipient.average_rating == 0.0

    Review.objects.create(
        task=task1,
        reviewer=reviewer1,
        recipient=recipient,
        rating=5,
        comment="Great work!",
    )
    recipient.refresh_from_db()
    assert recipient.average_rating == 5.0

    Review.objects.create(
        task=task2,
        reviewer=reviewer2,
        recipient=recipient,
        rating=3,
        comment="Good enough.",
    )
    recipient.refresh_from_db()
    assert recipient.average_rating == 4.0

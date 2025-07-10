import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_update_user_average_rating_on_review_creation(
    user_factory, task_factory, review_factory
):
    recipient = user_factory(email="recipient@test.com")
    reviewer1 = user_factory(email="reviewer1@test.com")
    reviewer2 = user_factory(email="reviewer2@test.com")

    task1 = task_factory(client=recipient)
    task2 = task_factory(client=recipient)

    assert recipient.average_rating == 0.0

    review_factory(
        task=task1,
        reviewer=reviewer1,
        recipient=recipient,
        rating=5,
        comment="Great work!",
    )
    recipient.refresh_from_db()
    assert recipient.average_rating == 5.0

    review_factory(
        task=task2,
        reviewer=reviewer2,
        recipient=recipient,
        rating=3,
        comment="Good enough.",
    )
    recipient.refresh_from_db()
    assert recipient.average_rating == 4.0

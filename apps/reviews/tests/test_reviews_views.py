import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from apps.reviews.models import Review
from apps.tasks.models import Task

User = get_user_model()


# ==================
#  review endpoints
# ==================


# list


def test_review_list_unauthenticated(api_client, review_factory):
    review = review_factory()
    response = api_client.get(reverse("tasks:task-reviews-list", args=[review.task.pk]))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "results" not in response.data


@pytest.mark.django_db
def test_review_list_success(api_client, reviews):
    api_client.force_authenticate(reviews[0].task.client)
    response = api_client.get(
        reverse("tasks:task-reviews-list", args=[reviews[0].task.pk])
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("results") is not None
    assert response.data.get("count") == 2  # Only two reviews for the first task


@pytest.mark.django_db
def test_review_list_task_not_found(api_client, client_user):
    api_client.force_authenticate(client_user)
    response = api_client.get(reverse("tasks:task-reviews-list", args=[0]))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "results" not in response.data


@pytest.mark.django_db
def test_review_list_filter_by_reviewer(api_client, client_user, reviews):
    api_client.force_authenticate(client_user)
    response = api_client.get(
        reverse("tasks:task-reviews-list", args=[reviews[0].task.pk]),
        {"reviewer": client_user.pk},
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data.get("results")) == 1
    assert response.data.get("results")[0]["reviewer"] == client_user.pk


@pytest.mark.django_db
def test_review_list_filter_by_recipient(api_client, freelancer_user, reviews):
    api_client.force_authenticate(reviews[0].task.client)
    response = api_client.get(
        reverse("tasks:task-reviews-list", args=[reviews[0].task.pk]),
        {"recipient": freelancer_user.pk},
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data.get("results")) == 1
    assert response.data.get("results")[0]["recipient"] == freelancer_user.pk


@pytest.mark.django_db
def test_review_list_search_by_comment(api_client, reviews):
    api_client.force_authenticate(reviews[0].task.client)
    response = api_client.get(
        reverse("tasks:task-reviews-list", args=[reviews[0].task.pk]),
        {"search": "Excellent work!"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data.get("results")) == 1
    assert response.data.get("results")[0]["comment"] == "Excellent work!"


@pytest.mark.django_db
def test_review_list_order_by_rating_desc(api_client, reviews):
    api_client.force_authenticate(reviews[0].task.client)
    response = api_client.get(
        reverse("tasks:task-reviews-list", args=[reviews[0].task.pk]),
        {"ordering": "-rating"},
    )

    assert response.status_code == status.HTTP_200_OK
    ratings = [review_data["rating"] for review_data in response.data.get("results")]
    assert ratings == sorted(ratings, reverse=True)


@pytest.mark.django_db
def test_review_list_order_by_rating_asc(api_client, reviews):
    api_client.force_authenticate(reviews[0].task.client)
    response = api_client.get(
        reverse("tasks:task-reviews-list", args=[reviews[0].task.pk]),
        {"ordering": "rating"},
    )

    assert response.status_code == status.HTTP_200_OK
    ratings = [review_data["rating"] for review_data in response.data.get("results")]
    assert ratings == sorted(ratings)


@pytest.mark.django_db
def test_review_list_order_by_created_at_desc(api_client, reviews):
    api_client.force_authenticate(reviews[0].task.client)
    response = api_client.get(
        reverse("tasks:task-reviews-list", args=[reviews[0].task.pk]),
        {"ordering": "-created_at"},
    )

    assert response.status_code == status.HTTP_200_OK
    created_at_list = [
        review_data["created_at"] for review_data in response.data.get("results")
    ]
    assert created_at_list == sorted(created_at_list, reverse=True)


@pytest.mark.django_db
def test_review_list_order_by_created_at_asc(api_client, reviews):
    api_client.force_authenticate(reviews[0].task.client)
    response = api_client.get(
        reverse("tasks:task-reviews-list", args=[reviews[0].task.pk]),
        {"ordering": "created_at"},
    )

    assert response.status_code == status.HTTP_200_OK
    created_at_list = [
        review_data["created_at"] for review_data in response.data.get("results")
    ]
    assert created_at_list == sorted(created_at_list)


# create


def test_review_create_unauthenticated(api_client, review_data, task_factory):
    task = task_factory()
    response = api_client.post(
        reverse("tasks:task-reviews-list", args=[task.pk]), review_data
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not "id" in review_data


@pytest.mark.django_db
def test_review_create_as_client_success(
    api_client, freelancer_user, review_data, task_factory
):
    task = task_factory(freelancer=freelancer_user, status=Task.TaskStatus.COMPLETED)
    api_client.force_authenticate(task.client)
    response = api_client.post(
        reverse("tasks:task-reviews-list", args=[task.pk]), review_data
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.data
    review = Review.objects.get(id=response.data.get("id"))
    assert review is not None
    assert review.reviewer == task.client
    assert review.recipient == task.freelancer


@pytest.mark.django_db
def test_review_create_as_freelancer_success(
    api_client, freelancer_user, review_data, task_factory
):
    task = task_factory(freelancer=freelancer_user, status=Task.TaskStatus.COMPLETED)
    api_client.force_authenticate(task.freelancer)
    response = api_client.post(
        reverse("tasks:task-reviews-list", args=[task.pk]), review_data
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.data
    review = Review.objects.get(id=response.data.get("id"))
    assert review is not None
    assert review.reviewer == task.freelancer
    assert review.recipient == task.client


@pytest.mark.django_db
def test_review_create_freelancer_is_not_assigned_fail(
    api_client, review_data, task_factory
):
    task = task_factory(status=Task.TaskStatus.COMPLETED)
    api_client.force_authenticate(task.client)
    response = api_client.post(
        reverse("tasks:task-reviews-list", args=[task.pk]), review_data
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not "id" in response.data
    assert not Review.objects.filter(reviewer=task.client).exists()


@pytest.mark.django_db
def test_review_create_task_is_not_completed_fail(
    api_client, freelancer_user, review_data, task_factory
):
    task = task_factory(freelancer=freelancer_user)
    api_client.force_authenticate(task.client)
    response = api_client.post(
        reverse("tasks:task-reviews-list", args=[task.pk]), review_data
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not "id" in response.data
    assert not Review.objects.filter(reviewer=task.client).exists()


@pytest.mark.django_db
def test_review_create_as_random_user_fail(
    api_client, freelancer_user, random_user, review_data, task_factory
):
    task = task_factory(freelancer=freelancer_user, status=Task.TaskStatus.COMPLETED)
    api_client.force_authenticate(random_user)
    response = api_client.post(
        reverse("tasks:task-reviews-list", args=[task.pk]), review_data
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not "id" in response.data
    assert not Review.objects.filter(reviewer=random_user).exists()


@pytest.mark.django_db
def test_review_create_violate_unique_constraint_fail(
    api_client, freelancer_user, review_data, review_factory, task_factory
):
    task = task_factory(freelancer=freelancer_user, status=Task.TaskStatus.COMPLETED)
    review = review_factory(task=task)
    api_client.force_authenticate(task.client)
    response = api_client.post(
        reverse("tasks:task-reviews-list", args=[task.pk]), review_data
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not "id" in response.data
    assert Review.objects.filter(reviewer=task.client).count() == 1


# retrieve


def test_review_retrieve_unauthenticated(api_client, review_factory):
    review = review_factory()
    response = api_client.get(
        reverse("tasks:task-reviews-detail", args=[review.task.pk, review.pk])
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not "id" in response.data


@pytest.mark.django_db
def test_review_retrieve_as_reviewer_success(api_client, review_factory):
    review = review_factory()
    api_client.force_authenticate(review.reviewer)
    response = api_client.get(
        reverse("tasks:task-reviews-detail", args=[review.task.pk, review.pk])
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == review.pk


@pytest.mark.django_db
def test_review_retrieve_as_recipient_success(api_client, review_factory):
    review = review_factory()
    api_client.force_authenticate(review.recipient)
    response = api_client.get(
        reverse("tasks:task-reviews-detail", args=[review.task.pk, review.pk])
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == review.pk


@pytest.mark.django_db
def test_review_retrieve_as_random_user_success(
    api_client, random_user, review_factory
):
    review = review_factory()
    api_client.force_authenticate(random_user)
    response = api_client.get(
        reverse("tasks:task-reviews-detail", args=[review.task.pk, review.pk])
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == review.pk


# update


def test_review_update_fail(api_client, review_factory):
    review = review_factory()
    api_client.force_authenticate(review.reviewer)
    response = api_client.patch(
        reverse("tasks:task-reviews-detail", args=[review.task.pk, review.pk]),
        {"comment": "UPDATED"},
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


# delete


def test_review_delete_fail(api_client, review_factory):
    review = review_factory()
    api_client.force_authenticate(review.reviewer)
    response = api_client.delete(
        reverse("tasks:task-reviews-detail", args=[review.task.pk, review.pk])
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

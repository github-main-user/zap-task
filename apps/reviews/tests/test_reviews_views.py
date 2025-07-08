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


def test_review_list_unauthenticated(api_client, task_obj, review_obj):
    response = api_client.get(reverse("tasks:task-reviews-list", args=[task_obj.pk]))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "results" not in response.data


@pytest.mark.django_db
def test_review_list_success(api_client, task_obj, review_obj):
    api_client.force_authenticate(task_obj.client)
    response = api_client.get(reverse("tasks:task-reviews-list", args=[task_obj.pk]))

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("results") is not None
    assert response.data.get("count") == task_obj.reviews.count()


@pytest.mark.django_db
def test_review_list_task_not_found(api_client, client_user):
    api_client.force_authenticate(client_user)
    response = api_client.get(reverse("tasks:task-reviews-list", args=[0]))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "results" not in response.data


# create


def test_review_create_unauthenticated(api_client, task_obj, review_data):
    response = api_client.post(
        reverse("tasks:task-reviews-list", args=[task_obj.pk]), review_data
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not "id" in review_data


@pytest.mark.django_db
def test_review_create_as_client_success(
    api_client, task_obj, freelancer_user, review_data
):
    task_obj.freelancer = freelancer_user
    task_obj.status = Task.TaskStatus.COMPLETED
    task_obj.save()
    api_client.force_authenticate(task_obj.client)
    response = api_client.post(
        reverse("tasks:task-reviews-list", args=[task_obj.pk]), review_data
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.data
    review = Review.objects.get(id=response.data.get("id"))
    assert review is not None
    assert review.reviewer == task_obj.client
    assert review.recipient == task_obj.freelancer


@pytest.mark.django_db
def test_review_create_as_freelancer_success(
    api_client, task_obj, freelancer_user, review_data
):
    task_obj.freelancer = freelancer_user
    task_obj.status = Task.TaskStatus.COMPLETED
    task_obj.save()
    api_client.force_authenticate(task_obj.freelancer)
    response = api_client.post(
        reverse("tasks:task-reviews-list", args=[task_obj.pk]), review_data
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.data
    review = Review.objects.get(id=response.data.get("id"))
    assert review is not None
    assert review.reviewer == task_obj.freelancer
    assert review.recipient == task_obj.client


@pytest.mark.django_db
def test_review_create_freelancer_is_not_assigned_fail(
    api_client, task_obj, review_data
):
    task_obj.status = Task.TaskStatus.COMPLETED
    task_obj.save()
    api_client.force_authenticate(task_obj.client)
    response = api_client.post(
        reverse("tasks:task-reviews-list", args=[task_obj.pk]), review_data
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not "id" in response.data
    assert not Review.objects.filter(reviewer=task_obj.client).exists()


@pytest.mark.django_db
def test_review_create_task_is_not_completed_fail(
    api_client, task_obj, freelancer_user, review_data
):
    task_obj.freelancer = freelancer_user
    task_obj.save()
    api_client.force_authenticate(task_obj.client)
    response = api_client.post(
        reverse("tasks:task-reviews-list", args=[task_obj.pk]), review_data
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not "id" in response.data
    assert not Review.objects.filter(reviewer=task_obj.client).exists()


@pytest.mark.django_db
def test_review_create_as_random_user_fail(
    api_client, task_obj, freelancer_user, review_data
):
    new_user = User.objects.create_user(
        email="new@user.com", password="pass", role=User.UserRole.CLIENT
    )
    task_obj.status = Task.TaskStatus.COMPLETED
    task_obj.freelancer = freelancer_user
    task_obj.save()
    api_client.force_authenticate(new_user)
    response = api_client.post(
        reverse("tasks:task-reviews-list", args=[task_obj.pk]), review_data
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not "id" in response.data
    assert not Review.objects.filter(reviewer=new_user).exists()


@pytest.mark.django_db
def test_review_create_violate_unique_constraint_fail(
    api_client, task_obj, freelancer_user, review_data, review_obj
):
    task_obj.status = Task.TaskStatus.COMPLETED
    task_obj.freelancer = freelancer_user
    task_obj.save()
    api_client.force_authenticate(task_obj.client)
    response = api_client.post(
        reverse("tasks:task-reviews-list", args=[task_obj.pk]), review_data
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not "id" in response.data
    assert Review.objects.filter(reviewer=task_obj.client).count() == 1


# retrieve


def test_review_retrieve_unauthenticated(api_client, review_obj):
    response = api_client.get(
        reverse("tasks:task-reviews-detail", args=[review_obj.task.pk, review_obj.pk])
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not "id" in response.data


@pytest.mark.django_db
def test_review_retrieve_as_reviewer_success(api_client, review_obj):
    api_client.force_authenticate(review_obj.reviewer)
    response = api_client.get(
        reverse("tasks:task-reviews-detail", args=[review_obj.task.pk, review_obj.pk])
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == review_obj.pk


@pytest.mark.django_db
def test_review_retrieve_as_recipient_success(api_client, review_obj):
    api_client.force_authenticate(review_obj.recipient)
    response = api_client.get(
        reverse("tasks:task-reviews-detail", args=[review_obj.task.pk, review_obj.pk])
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == review_obj.pk


@pytest.mark.django_db
def test_review_retrieve_as_random_user_success(api_client, review_obj):
    new_user = User.objects.create_user(
        email="new@user.com", password="pass", role=User.UserRole.CLIENT
    )
    api_client.force_authenticate(new_user)
    response = api_client.get(
        reverse("tasks:task-reviews-detail", args=[review_obj.task.pk, review_obj.pk])
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == review_obj.pk


# update


def test_review_update_fail(api_client, review_obj):
    api_client.force_authenticate(review_obj.reviewer)
    response = api_client.patch(
        reverse(
            "tasks:task-reviews-detail", args=[review_obj.task.pk, review_obj.pk]
        ),
        {"comment": "UPDATED"},
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


# delete


def test_review_delete_fail(api_client, review_obj):
    api_client.force_authenticate(review_obj.reviewer)
    response = api_client.delete(
        reverse("tasks:task-reviews-detail", args=[review_obj.task.pk, review_obj.pk])
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from apps.tasks.models import Task

User = get_user_model()


# ================
#  task endpoints
# ================


# list


@pytest.mark.django_db
def test_task_list_unauthenticated(api_client, tasks):
    response = api_client.get(reverse("tasks:task-list"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("count") == len(tasks)
    assert "results" in response.data


@pytest.mark.django_db
def test_task_list_success(api_client, client_user, tasks):
    api_client.force_authenticate(client_user)
    response = api_client.get(reverse("tasks:task-list"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("count") == len(tasks)
    assert "results" in response.data


@pytest.mark.django_db
def test_task_list_filter_by_status(api_client, client_user, tasks):
    api_client.force_authenticate(client_user)
    response = api_client.get(
        reverse("tasks:task-list"), {"status": Task.TaskStatus.OPEN}
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data.get("results")) == 2  # Two open tasks in conftest
    for task_data in response.data.get("results"):
        assert task_data["status"] == Task.TaskStatus.OPEN


@pytest.mark.django_db
def test_task_list_filter_by_client(api_client, client_user, tasks):
    api_client.force_authenticate(client_user)
    response = api_client.get(reverse("tasks:task-list"), {"client": client_user.pk})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data.get("results")) == 5  # Five tasks created by client_user
    for task_data in response.data.get("results"):
        assert task_data["client"] == client_user.pk


@pytest.mark.django_db
def test_task_list_filter_by_freelancer(
    api_client, client_user, freelancer_user, tasks
):
    api_client.force_authenticate(client_user)
    response = api_client.get(
        reverse("tasks:task-list"), {"freelancer": freelancer_user.pk}
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        len(response.data.get("results")) == 3
    )  # Three tasks assigned to freelancer_user
    for task_data in response.data.get("results"):
        assert task_data["freelancer"] == freelancer_user.pk


@pytest.mark.django_db
def test_task_list_search_by_title(api_client, client_user, tasks):
    api_client.force_authenticate(client_user)
    response = api_client.get(reverse("tasks:task-list"), {"search": "Open Task 1"})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data.get("results")) == 1
    assert response.data.get("results")[0]["title"] == "Open Task 1"


@pytest.mark.django_db
def test_task_list_search_by_description(api_client, client_user, tasks):
    api_client.force_authenticate(client_user)
    response = api_client.get(
        reverse("tasks:task-list"), {"search": "Description for in progress task 2"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data.get("results")) == 1
    assert (
        response.data.get("results")[0]["description"]
        == "Description for in progress task 2"
    )


@pytest.mark.django_db
def test_task_list_order_by_price_desc(api_client, client_user, tasks):
    api_client.force_authenticate(client_user)
    response = api_client.get(reverse("tasks:task-list"), {"ordering": "-price"})

    assert response.status_code == status.HTTP_200_OK
    prices = [float(task_data["price"]) for task_data in response.data.get("results")]
    assert prices == sorted(prices, reverse=True)


@pytest.mark.django_db
def test_task_list_order_by_deadline_asc(api_client, client_user, tasks):
    api_client.force_authenticate(client_user)
    response = api_client.get(reverse("tasks:task-list"), {"ordering": "deadline"})

    assert response.status_code == status.HTTP_200_OK
    deadlines = [task_data["deadline"] for task_data in response.data.get("results")]
    assert deadlines == sorted(deadlines)


# create


@pytest.mark.django_db
def test_task_create_unauthenticated(api_client, task_data):
    response = api_client.post(reverse("tasks:task-list"), task_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not Task.objects.filter(title=task_data["title"]).exists()


@pytest.mark.django_db
def test_task_create_as_client_success(api_client, client_user, task_data):
    api_client.force_authenticate(client_user)
    response = api_client.post(reverse("tasks:task-list"), task_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert Task.objects.get(title=task_data["title"]).client == client_user


@pytest.mark.django_db
def test_task_create_as_freelancer_fail(api_client, freelancer_user, task_data):
    api_client.force_authenticate(freelancer_user)
    response = api_client.post(reverse("tasks:task-list"), task_data)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not Task.objects.filter(title=task_data["title"]).exists()


@pytest.mark.django_db
def test_task_create_deadline_in_past_fail(api_client, client_user, task_data):
    api_client.force_authenticate(client_user)
    response = api_client.post(
        reverse("tasks:task-list"), task_data | {"deadline": "1970-12-31"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not Task.objects.filter(title=task_data["title"]).exists()


@pytest.mark.django_db
def test_task_create_negative_price_fail(api_client, client_user, task_data):
    api_client.force_authenticate(client_user)
    response = api_client.post(
        reverse("tasks:task-list"), task_data | {"price": -10.00}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not Task.objects.filter(title=task_data["title"]).exists()


# retrieve


@pytest.mark.django_db
def test_task_retrieve_not_found(api_client, client_user):
    api_client.force_authenticate(client_user)
    response = api_client.get(reverse("tasks:task-detail", args=[0]))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "id" not in response.data


def test_task_retrieve_unauthenticated(api_client, task_factory):
    task = task_factory()
    response = api_client.get(reverse("tasks:task-detail", args=[task.pk]))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "id" not in response.data


@pytest.mark.django_db
def test_task_retrieve_success(api_client, client_user, task_factory):
    task = task_factory()
    api_client.force_authenticate(client_user)
    response = api_client.get(reverse("tasks:task-detail", args=[task.pk]))

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == task.pk


# update


@pytest.mark.django_db
def test_task_update_not_found(api_client, client_user):
    api_client.force_authenticate(client_user)
    response = api_client.patch(
        reverse("tasks:task-detail", args=[0]), {"title": "UPDATED"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "id" not in response.data


def test_task_update_unauthenticated(api_client, task_factory):
    task = task_factory()
    response = api_client.patch(
        reverse("tasks:task-detail", args=[task.pk]), {"title": "UPDATED"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "id" not in response.data
    task.refresh_from_db()
    assert task.title != "UPDATED"


@pytest.mark.django_db
def test_task_update_as_owner_success(api_client, client_user, task_factory):
    task = task_factory()
    api_client.force_authenticate(client_user)
    response = api_client.patch(
        reverse("tasks:task-detail", args=[task.pk]), {"title": "UPDATED"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == task.pk
    task.refresh_from_db()
    assert task.title == "UPDATED"


@pytest.mark.django_db
def test_task_update_as_random_user_fail(api_client, random_user, task_factory):
    task = task_factory()
    api_client.force_authenticate(random_user)
    response = api_client.patch(
        reverse("tasks:task-detail", args=[task.pk]), {"title": "UPDATED"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "id" not in response.data
    task.refresh_from_db()
    assert not task.title == "UPDATED"


@pytest.mark.django_db
def test_task_update_status_is_not_open_fail(api_client, client_user, task_factory):
    task = task_factory(status=Task.TaskStatus.COMPLETED)
    api_client.force_authenticate(client_user)
    response = api_client.patch(
        reverse("tasks:task-detail", args=[task.pk]), {"title": "UPDATED"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "id" not in response.data
    task.refresh_from_db()
    assert not task.title == "UPDATED"


# delete


@pytest.mark.django_db
def test_task_delete_not_found(api_client, client_user):
    api_client.force_authenticate(client_user)
    response = api_client.delete(reverse("tasks:task-detail", args=[0]))

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_task_delete_unauthenticated(api_client, task_factory):
    task = task_factory()
    response = api_client.delete(reverse("tasks:task-detail", args=[task.pk]))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Task.objects.filter(pk=task.pk).exists()


@pytest.mark.django_db
def test_task_delete_as_owner_success(api_client, client_user, task_factory):
    task = task_factory()
    api_client.force_authenticate(client_user)
    response = api_client.delete(reverse("tasks:task-detail", args=[task.pk]))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Task.objects.filter(pk=task.pk).exists()


@pytest.mark.django_db
def test_task_delete_as_random_user_fail(api_client, random_user, task_factory):
    task = task_factory()
    api_client.force_authenticate(random_user)
    response = api_client.delete(reverse("tasks:task-detail", args=[task.pk]))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Task.objects.filter(pk=task.pk).exists()


@pytest.mark.django_db
def test_task_delete_task_completed_fail(api_client, client_user, task_factory):
    task = task_factory(status=Task.TaskStatus.COMPLETED)
    api_client.force_authenticate(client_user)
    response = api_client.delete(reverse("tasks:task-detail", args=[task.pk]))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Task.objects.filter(pk=task.pk).exists()


# start


@pytest.mark.django_db
def test_task_start_as_freelancer_success(api_client, freelancer_user, task_factory):
    task = task_factory(freelancer=freelancer_user, status=Task.TaskStatus.PAID)
    api_client.force_authenticate(freelancer_user)
    response = api_client.post(reverse("tasks:task-start", args=[task.pk]))

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == task.pk
    task.refresh_from_db()
    assert task.status == Task.TaskStatus.IN_PROGRESS


@pytest.mark.django_db
def test_task_start_as_random_user_fail(api_client, random_user, task_factory):
    task = task_factory()
    api_client.force_authenticate(random_user)
    response = api_client.post(reverse("tasks:task-start", args=[task.pk]))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "id" not in response.data
    task.refresh_from_db()
    assert task.status == Task.TaskStatus.OPEN


@pytest.mark.django_db
def test_task_start_task_not_paid_fail(api_client, freelancer_user, task_factory):
    task = task_factory(freelancer=freelancer_user)
    api_client.force_authenticate(freelancer_user)
    response = api_client.post(reverse("tasks:task-start", args=[task.pk]))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "id" not in response.data
    task.refresh_from_db()
    assert task.status == Task.TaskStatus.OPEN


# submit


@pytest.mark.django_db
def test_task_submit_as_freelancer_success(api_client, freelancer_user, task_factory):
    task = task_factory(freelancer=freelancer_user, status=Task.TaskStatus.IN_PROGRESS)
    api_client.force_authenticate(freelancer_user)
    response = api_client.post(reverse("tasks:task-submit", args=[task.pk]))

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == task.pk
    task.refresh_from_db()
    assert task.status == Task.TaskStatus.PENDING_REVIEW


@pytest.mark.django_db
def test_task_submit_as_random_freelancer_fail(api_client, random_user, task_factory):
    task = task_factory(status=Task.TaskStatus.IN_PROGRESS)
    api_client.force_authenticate(random_user)
    response = api_client.post(reverse("tasks:task-submit", args=[task.pk]))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "id" not in response.data
    task.refresh_from_db()
    assert task.status == Task.TaskStatus.IN_PROGRESS


@pytest.mark.django_db
def test_task_submit_task_not_in_progress_fail(
    api_client, freelancer_user, task_factory
):
    task = task_factory(freelancer=freelancer_user, status=Task.TaskStatus.COMPLETED)
    api_client.force_authenticate(freelancer_user)
    response = api_client.post(reverse("tasks:task-submit", args=[task.pk]))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "id" not in response.data
    task.refresh_from_db()
    assert task.status == Task.TaskStatus.COMPLETED


# approve_submission


@pytest.mark.django_db
def test_task_approve_submission_as_task_client_success(
    api_client, freelancer_user, client_user, task_factory
):
    task = task_factory(
        freelancer=freelancer_user, status=Task.TaskStatus.PENDING_REVIEW
    )
    api_client.force_authenticate(client_user)
    response = api_client.post(reverse("tasks:task-approve-submission", args=[task.pk]))

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == task.pk
    task.refresh_from_db()
    assert task.status == Task.TaskStatus.COMPLETED


@pytest.mark.django_db
def test_task_approve_submission_as_random_user_fail(
    api_client, random_user, task_factory
):
    task = task_factory(status=Task.TaskStatus.PENDING_REVIEW)
    api_client.force_authenticate(random_user)
    response = api_client.post(reverse("tasks:task-approve-submission", args=[task.pk]))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "id" not in response.data
    task.refresh_from_db()
    assert task.status == Task.TaskStatus.PENDING_REVIEW


@pytest.mark.django_db
def test_task_approve_submission_task_not_pending_review_fail(
    api_client, freelancer_user, client_user, task_factory
):
    task = task_factory(freelancer=freelancer_user, status=Task.TaskStatus.COMPLETED)
    api_client.force_authenticate(client_user)
    response = api_client.post(reverse("tasks:task-approve-submission", args=[task.pk]))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "id" not in response.data
    task.refresh_from_db()
    assert task.status == Task.TaskStatus.COMPLETED


# reject_submission


@pytest.mark.django_db
def test_task_reject_submission_as_task_client_success(
    api_client, freelancer_user, client_user, task_factory
):
    task = task_factory(
        freelancer=freelancer_user, status=Task.TaskStatus.PENDING_REVIEW
    )
    api_client.force_authenticate(client_user)
    response = api_client.post(reverse("tasks:task-reject-submission", args=[task.pk]))

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == task.pk
    task.refresh_from_db()
    assert task.status == Task.TaskStatus.IN_PROGRESS


@pytest.mark.django_db
def test_task_reject_submission_as_random_user_fail(
    api_client, random_user, task_factory
):
    task = task_factory(status=Task.TaskStatus.PENDING_REVIEW)
    api_client.force_authenticate(random_user)
    response = api_client.post(reverse("tasks:task-reject-submission", args=[task.pk]))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "id" not in response.data
    task.refresh_from_db()
    assert task.status == Task.TaskStatus.PENDING_REVIEW


@pytest.mark.django_db
def test_task_reject_submission_task_not_pending_review_fail(
    api_client, freelancer_user, client_user, task_factory
):
    task = task_factory(freelancer=freelancer_user, status=Task.TaskStatus.COMPLETED)
    api_client.force_authenticate(client_user)
    response = api_client.post(reverse("tasks:task-reject-submission", args=[task.pk]))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "id" not in response.data
    task.refresh_from_db()
    assert task.status == Task.TaskStatus.COMPLETED


# cancel


@pytest.mark.django_db
def test_task_cancel_as_task_client_success(
    api_client, freelancer_user, client_user, task_factory
):
    task = task_factory(freelancer=freelancer_user)
    api_client.force_authenticate(client_user)
    response = api_client.post(reverse("tasks:task-cancel", args=[task.pk]))

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == task.pk
    task.refresh_from_db()
    assert task.status == Task.TaskStatus.CANCELED


@pytest.mark.django_db
def test_task_cancel_as_task_freelancer_success(
    api_client, freelancer_user, task_factory
):
    task = task_factory(freelancer=freelancer_user)
    api_client.force_authenticate(freelancer_user)
    response = api_client.post(reverse("tasks:task-cancel", args=[task.pk]))

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == task.pk
    task.refresh_from_db()
    assert task.status == Task.TaskStatus.CANCELED


@pytest.mark.django_db
def test_task_cancel_as_random_freelancer_fail(api_client, random_user, task_factory):
    task = task_factory()
    api_client.force_authenticate(random_user)
    response = api_client.post(reverse("tasks:task-cancel", args=[task.pk]))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "id" not in response.data
    task.refresh_from_db()
    assert task.status == Task.TaskStatus.OPEN


@pytest.mark.django_db
def test_task_cancel_not_open_fail(
    api_client, client_user, freelancer_user, task_factory
):
    task = task_factory(freelancer=freelancer_user, status=Task.TaskStatus.COMPLETED)
    api_client.force_authenticate(client_user)
    response = api_client.post(reverse("tasks:task-cancel", args=[task.pk]))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "id" not in response.data
    task.refresh_from_db()
    assert task.status == Task.TaskStatus.COMPLETED


# pay


@pytest.mark.django_db
@patch(
    "apps.tasks.views.StripeService.create_checkout_session",
    return_value="http://checkout.url",
)
def test_task_pay_success(
    mock_create_checkout_session, api_client, client_user, freelancer_user, task_factory
):
    task = task_factory(freelancer=freelancer_user)
    api_client.force_authenticate(client_user)
    response = api_client.post(reverse("tasks:task-pay", args=[task.pk]))

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("checkout_url") == "http://checkout.url"
    mock_create_checkout_session.assert_called_once_with(task)


@pytest.mark.django_db
def test_task_pay_as_random_user_fail(api_client, random_user, task_factory):
    task = task_factory()
    api_client.force_authenticate(random_user)
    response = api_client.post(reverse("tasks:task-pay", args=[task.pk]))

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_task_pay_no_freelancer_assigned_fail(api_client, client_user, task_factory):
    task = task_factory()
    api_client.force_authenticate(client_user)
    response = api_client.post(reverse("tasks:task-pay", args=[task.pk]))

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_task_pay_task_not_open_fail(
    api_client, client_user, freelancer_user, task_factory
):
    task = task_factory(freelancer=freelancer_user, status=Task.TaskStatus.PAID)
    api_client.force_authenticate(client_user)
    response = api_client.post(reverse("tasks:task-pay", args=[task.pk]))

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@patch("apps.tasks.views.StripeService.create_checkout_session", return_value=None)
def test_task_pay_create_checkout_session_fails(
    mock_create_checkout_session, api_client, client_user, freelancer_user, task_factory
):
    task = task_factory(freelancer=freelancer_user)
    api_client.force_authenticate(client_user)
    response = api_client.post(reverse("tasks:task-pay", args=[task.pk]))

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    mock_create_checkout_session.assert_called_once_with(task)

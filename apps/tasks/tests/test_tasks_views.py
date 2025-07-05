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


def test_task_list_unauthenticated(api_client):
    response = api_client.get(reverse("tasks:task-list"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "results" not in response.data


@pytest.mark.django_db
def test_task_list_success(api_client, client_user, tasks):
    api_client.force_authenticate(client_user)
    response = api_client.get(reverse("tasks:task-list"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("count") == len(tasks)
    assert "results" in response.data


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


# retrieve


@pytest.mark.django_db
def test_task_retrieve_not_found(api_client, client_user):
    api_client.force_authenticate(client_user)
    response = api_client.get(reverse("tasks:task-detail", args=[0]))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "id" not in response.data


@pytest.mark.django_db
def test_task_retrieve_unauthenticated(api_client, task_obj):
    response = api_client.get(reverse("tasks:task-detail", args=[task_obj.pk]))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "id" not in response.data


@pytest.mark.django_db
def test_task_retrieve_success(api_client, client_user, task_obj):
    api_client.force_authenticate(client_user)
    response = api_client.get(reverse("tasks:task-detail", args=[task_obj.pk]))

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == task_obj.pk


# update


@pytest.mark.django_db
def test_task_update_not_found(api_client, client_user):
    api_client.force_authenticate(client_user)
    response = api_client.patch(
        reverse("tasks:task-detail", args=[0]), {"title": "UPDATED"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "id" not in response.data


@pytest.mark.django_db
def test_task_update_unauthenticated(api_client, task_obj):
    response = api_client.patch(
        reverse("tasks:task-detail", args=[task_obj.pk]), {"title": "UPDATED"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "id" not in response.data
    task_obj.refresh_from_db()
    assert task_obj.title != "UPDATED"


@pytest.mark.django_db
def test_task_update_as_owner_success(api_client, client_user, task_obj):
    api_client.force_authenticate(client_user)
    response = api_client.patch(
        reverse("tasks:task-detail", args=[task_obj.pk]), {"title": "UPDATED"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == task_obj.pk
    task_obj.refresh_from_db()
    assert task_obj.title == "UPDATED"


@pytest.mark.django_db
def test_task_update_as_foreign_user_fail(api_client, freelancer_user, task_obj):
    api_client.force_authenticate(freelancer_user)
    response = api_client.patch(
        reverse("tasks:task-detail", args=[task_obj.pk]), {"title": "UPDATED"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "id" not in response.data
    task_obj.refresh_from_db()
    assert not task_obj.title == "UPDATED"


@pytest.mark.django_db
def test_task_update_status_is_not_open_fail(api_client, client_user, task_obj):
    task_obj.status = Task.TaskStatus.COMPLETED
    task_obj.save()
    api_client.force_authenticate(client_user)
    response = api_client.patch(
        reverse("tasks:task-detail", args=[task_obj.pk]), {"title": "UPDATED"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "id" not in response.data
    task_obj.refresh_from_db()
    assert not task_obj.title == "UPDATED"


# delete


@pytest.mark.django_db
def test_task_delete_not_found(api_client, client_user):
    api_client.force_authenticate(client_user)
    response = api_client.delete(reverse("tasks:task-detail", args=[0]))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_task_delete_unauthenticated(api_client, task_obj):
    response = api_client.delete(reverse("tasks:task-detail", args=[task_obj.pk]))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Task.objects.filter(id=task_obj.pk).exists()


@pytest.mark.django_db
def test_task_delete_as_owner_success(api_client, client_user, task_obj):
    api_client.force_authenticate(client_user)
    response = api_client.delete(reverse("tasks:task-detail", args=[task_obj.pk]))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Task.objects.filter(id=task_obj.pk).exists()


@pytest.mark.django_db
def test_task_delete_as_foreign_user_fail(api_client, freelancer_user, task_obj):
    api_client.force_authenticate(freelancer_user)
    response = api_client.delete(reverse("tasks:task-detail", args=[task_obj.pk]))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Task.objects.filter(id=task_obj.pk).exists()


@pytest.mark.django_db
def test_task_delete_task_completed_fail(api_client, client_user, task_obj):
    task_obj.status = Task.TaskStatus.COMPLETED
    task_obj.save()
    api_client.force_authenticate(client_user)
    response = api_client.delete(reverse("tasks:task-detail", args=[task_obj.pk]))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Task.objects.filter(id=task_obj.pk).exists()

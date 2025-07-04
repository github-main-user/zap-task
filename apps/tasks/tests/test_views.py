import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from apps.tasks.models import Proposal, Task

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
def proposal_data():
    return {"message": "Proposal Message"}


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
            **task_data,
            status=Task.TaskStatus.OPEN,
            client=client_user,
        ),
        Task.objects.create(
            **task_data,
            status=Task.TaskStatus.COMPLETED,
            client=client_user,
            freelancer=freelancer_user,
        ),
    )


@pytest.fixture
def proposal_obj(db, proposal_data, task_obj, freelancer_user):
    return Proposal.objects.create(
        **proposal_data, task=task_obj, freelancer=freelancer_user
    )


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
    response = api_client.get(reverse("tasks:task-detail", args=[task_obj.id]))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "id" not in response.data


@pytest.mark.django_db
def test_task_retrieve_success(api_client, client_user, task_obj):
    api_client.force_authenticate(client_user)
    response = api_client.get(reverse("tasks:task-detail", args=[task_obj.id]))

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == task_obj.id


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
        reverse("tasks:task-detail", args=[task_obj.id]), {"title": "UPDATED"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "id" not in response.data
    task_obj.refresh_from_db()
    assert task_obj.title != "UPDATED"


@pytest.mark.django_db
def test_task_update_as_owner_success(api_client, client_user, task_obj):
    api_client.force_authenticate(client_user)
    response = api_client.patch(
        reverse("tasks:task-detail", args=[task_obj.id]), {"title": "UPDATED"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == task_obj.id
    task_obj.refresh_from_db()
    assert task_obj.title == "UPDATED"


@pytest.mark.django_db
def test_task_update_as_foreign_user_fail(api_client, freelancer_user, task_obj):
    api_client.force_authenticate(freelancer_user)
    response = api_client.patch(
        reverse("tasks:task-detail", args=[task_obj.id]), {"title": "UPDATED"}
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
        reverse("tasks:task-detail", args=[task_obj.id]), {"title": "UPDATED"}
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
    response = api_client.delete(reverse("tasks:task-detail", args=[task_obj.id]))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Task.objects.filter(id=task_obj.id).exists()


@pytest.mark.django_db
def test_task_delete_as_owner_success(api_client, client_user, task_obj):
    api_client.force_authenticate(client_user)
    response = api_client.delete(reverse("tasks:task-detail", args=[task_obj.id]))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Task.objects.filter(id=task_obj.id).exists()


@pytest.mark.django_db
def test_task_delete_as_foreign_user_fail(api_client, freelancer_user, task_obj):
    api_client.force_authenticate(freelancer_user)
    response = api_client.delete(reverse("tasks:task-detail", args=[task_obj.id]))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Task.objects.filter(id=task_obj.id).exists()


@pytest.mark.django_db
def test_task_delete_task_completed_fail(api_client, client_user, task_obj):
    task_obj.status = Task.TaskStatus.COMPLETED
    task_obj.save()
    api_client.force_authenticate(client_user)
    response = api_client.delete(reverse("tasks:task-detail", args=[task_obj.id]))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Task.objects.filter(id=task_obj.id).exists()


# ====================
#  proposal endpoints
# ====================


# list


@pytest.mark.django_db
def test_proposal_list_unauthenticated(api_client, proposal_obj):
    response = api_client.get(
        reverse("tasks:task-proposals-list", args=[proposal_obj.task.id])
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "results" not in response.data


@pytest.mark.django_db
def test_proposal_list_success(api_client, client_user, proposal_obj):
    api_client.force_authenticate(client_user)
    response = api_client.get(
        reverse("tasks:task-proposals-list", args=[proposal_obj.task.id])
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("count") == 1
    assert "results" in response.data


# create


@pytest.mark.django_db
def test_proposal_create_unauthenticated(api_client, task_obj, proposal_data):
    response = api_client.post(
        reverse("tasks:task-proposals-list", args=[task_obj.id]), proposal_data
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not Proposal.objects.filter(message=proposal_data["message"]).exists()


@pytest.mark.django_db
def test_proposal_create_as_freelancer_success(
    api_client, freelancer_user, task_obj, proposal_data
):
    api_client.force_authenticate(freelancer_user)
    response = api_client.post(
        reverse("tasks:task-proposals-list", args=[task_obj.id]), proposal_data
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert (
        Proposal.objects.get(message=proposal_data["message"]).freelancer
        == freelancer_user
    )


@pytest.mark.django_db
def test_proposal_create_already_exists_for_this_task_fail(
    api_client, freelancer_user, proposal_obj
):
    api_client.force_authenticate(freelancer_user)
    response = api_client.post(
        reverse("tasks:task-proposals-list", args=[proposal_obj.task.id]),
        {"message": proposal_obj.message},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Proposal.objects.filter(message=proposal_obj.message).count() == 1


@pytest.mark.django_db
def test_proposal_create_as_client_fail(
    api_client, client_user, task_obj, proposal_data
):
    api_client.force_authenticate(client_user)
    response = api_client.post(
        reverse("tasks:task-proposals-list", args=[task_obj.id]), proposal_data
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not Proposal.objects.filter(message=proposal_data["message"]).exists()


# retrieve


@pytest.mark.django_db
def test_proposal_retrieve_not_found(api_client, freelancer_user):
    api_client.force_authenticate(freelancer_user)
    response = api_client.get(reverse("tasks:task-proposals-detail", args=[0, 0]))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "id" not in response.data


@pytest.mark.django_db
def test_proposal_retrieve_unauthenticated(api_client):
    response = api_client.get(reverse("tasks:task-proposals-detail", args=[0, 0]))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "id" not in response.data


@pytest.mark.django_db
def test_proposal_retrieve_as_proposal_task_owner_success(
    api_client, client_user, proposal_obj
):
    api_client.force_authenticate(client_user)
    response = api_client.get(
        reverse(
            "tasks:task-proposals-detail", args=[proposal_obj.task.id, proposal_obj.id]
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == proposal_obj.id


@pytest.mark.django_db
def test_proposal_retrieve_as_proposal_owner_success(
    api_client, freelancer_user, proposal_obj
):
    api_client.force_authenticate(freelancer_user)
    response = api_client.get(
        reverse(
            "tasks:task-proposals-detail", args=[proposal_obj.task.id, proposal_obj.id]
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == proposal_obj.id


@pytest.mark.django_db
def test_proposal_retrieve_as_foreign_user_fail(api_client, proposal_obj):
    temp_user = User.objects.create_user(
        email="email@email.com", password="password", role=User.UserRole.CLIENT
    )
    api_client.force_authenticate(temp_user)
    response = api_client.get(
        reverse(
            "tasks:task-proposals-detail", args=[proposal_obj.task.id, proposal_obj.id]
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "id" not in response.data


# update


@pytest.mark.django_db
def test_proposal_update_not_found(api_client, freelancer_user):
    api_client.force_authenticate(freelancer_user)
    response = api_client.patch(
        reverse("tasks:task-proposals-detail", args=[0, 0]), {"message": "UPDATED"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "id" not in response.data


@pytest.mark.django_db
def test_proposal_update_unauthenticated(api_client, proposal_obj):
    response = api_client.patch(
        reverse(
            "tasks:task-proposals-detail", args=[proposal_obj.task.id, proposal_obj.id]
        ),
        {"message": "UPDATED"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "id" not in response.data
    proposal_obj.refresh_from_db()
    assert proposal_obj.message != "UPDATED"


@pytest.mark.django_db
def test_proposal_update_as_owner_success(api_client, freelancer_user, proposal_obj):
    api_client.force_authenticate(freelancer_user)
    response = api_client.patch(
        reverse(
            "tasks:task-proposals-detail", args=[proposal_obj.task.id, proposal_obj.id]
        ),
        {"message": "UPDATED"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == proposal_obj.id
    proposal_obj.refresh_from_db()
    assert proposal_obj.message == "UPDATED"


@pytest.mark.django_db
def test_proposal_update_as_foreign_user_fail(api_client, client_user, proposal_obj):
    api_client.force_authenticate(client_user)
    response = api_client.patch(
        reverse(
            "tasks:task-proposals-detail", args=[proposal_obj.task.id, proposal_obj.id]
        ),
        {"message": "UPDATED"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "id" not in response.data
    proposal_obj.refresh_from_db()
    assert proposal_obj.message != "UPDATED"


@pytest.mark.django_db
def test_proposal_update_status_is_not_pending_fail(
    api_client, freelancer_user, proposal_obj
):
    proposal_obj.status = Proposal.ProposalStatus.ACCEPTED
    proposal_obj.save()
    api_client.force_authenticate(freelancer_user)
    response = api_client.patch(
        reverse(
            "tasks:task-proposals-detail", args=[proposal_obj.task.id, proposal_obj.id]
        ),
        {"message": "UPDATED"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "id" not in response.data
    proposal_obj.refresh_from_db()
    assert proposal_obj.message != "UPDATED"


# delete


@pytest.mark.django_db
def test_proposal_delete_not_found(api_client, freelancer_user):
    api_client.force_authenticate(freelancer_user)
    response = api_client.delete(reverse("tasks:task-proposals-detail", args=[0, 0]))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_proposal_delete_unauthenticated(api_client, proposal_obj):
    response = api_client.delete(
        reverse(
            "tasks:task-proposals-detail", args=[proposal_obj.task.id, proposal_obj.id]
        )
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Proposal.objects.filter(id=proposal_obj.id).exists()


@pytest.mark.django_db
def test_proposal_delete_as_owner_success(api_client, freelancer_user, proposal_obj):
    api_client.force_authenticate(freelancer_user)
    response = api_client.delete(
        reverse(
            "tasks:task-proposals-detail", args=[proposal_obj.task.id, proposal_obj.id]
        )
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Proposal.objects.filter(id=proposal_obj.id).exists()


@pytest.mark.django_db
def test_proposal_delete_as_foreign_user_fail(api_client, client_user, proposal_obj):
    api_client.force_authenticate(client_user)
    response = api_client.delete(
        reverse(
            "tasks:task-proposals-detail", args=[proposal_obj.task.id, proposal_obj.id]
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Proposal.objects.filter(id=proposal_obj.id).exists()


@pytest.mark.django_db
def test_proposal_delete_is_not_pending_fail(api_client, client_user, proposal_obj):
    proposal_obj.status = Proposal.ProposalStatus.ACCEPTED
    proposal_obj.save()
    api_client.force_authenticate(client_user)
    response = api_client.delete(
        reverse(
            "tasks:task-proposals-detail", args=[proposal_obj.task.id, proposal_obj.id]
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Proposal.objects.filter(id=proposal_obj.id).exists()

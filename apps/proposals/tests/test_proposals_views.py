import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from apps.proposals.models import Proposal
from apps.tasks.models import Task

User = get_user_model()


# ====================
#  proposal endpoints
# ====================


# list


def test_proposal_list_unauthenticated(api_client, proposal_obj):
    response = api_client.get(
        reverse("proposals:task-proposals-list", args=[proposal_obj.task.pk])
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "results" not in response.data


@pytest.mark.django_db
def test_proposal_list_success(api_client, client_user, proposal_obj):
    api_client.force_authenticate(client_user)
    response = api_client.get(
        reverse("proposals:task-proposals-list", args=[proposal_obj.task.pk])
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("count") == 1
    assert "results" in response.data


# create


def test_proposal_create_unauthenticated(api_client, task_obj, proposal_data):
    response = api_client.post(
        reverse("proposals:task-proposals-list", args=[task_obj.pk]), proposal_data
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not Proposal.objects.filter(message=proposal_data["message"]).exists()


@pytest.mark.django_db
def test_proposal_create_as_freelancer_success(
    api_client, freelancer_user, task_obj, proposal_data
):
    api_client.force_authenticate(freelancer_user)
    response = api_client.post(
        reverse("proposals:task-proposals-list", args=[task_obj.pk]), proposal_data
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
        reverse("proposals:task-proposals-list", args=[proposal_obj.task.pk]),
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
        reverse("proposals:task-proposals-list", args=[task_obj.pk]), proposal_data
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not Proposal.objects.filter(message=proposal_data["message"]).exists()


@pytest.mark.django_db
def test_proposal_create_task_is_not_open_fail(
    api_client, client_user, task_obj, proposal_data
):
    task_obj.status = Task.TaskStatus.IN_PROGRESS
    task_obj.save()
    api_client.force_authenticate(client_user)
    response = api_client.post(
        reverse("proposals:task-proposals-list", args=[task_obj.pk]), proposal_data
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not Proposal.objects.filter(message=proposal_data["message"]).exists()


# retrieve


@pytest.mark.django_db
def test_proposal_retrieve_not_found(api_client, freelancer_user):
    api_client.force_authenticate(freelancer_user)
    response = api_client.get(reverse("proposals:task-proposals-detail", args=[0, 0]))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "id" not in response.data


def test_proposal_retrieve_unauthenticated(api_client):
    response = api_client.get(reverse("proposals:task-proposals-detail", args=[0, 0]))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "id" not in response.data


@pytest.mark.django_db
def test_proposal_retrieve_as_proposal_task_owner_success(
    api_client, client_user, proposal_obj
):
    api_client.force_authenticate(client_user)
    response = api_client.get(
        reverse(
            "proposals:task-proposals-detail",
            args=[proposal_obj.task.pk, proposal_obj.pk],
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == proposal_obj.pk


@pytest.mark.django_db
def test_proposal_retrieve_as_proposal_owner_success(
    api_client, freelancer_user, proposal_obj
):
    api_client.force_authenticate(freelancer_user)
    response = api_client.get(
        reverse(
            "proposals:task-proposals-detail",
            args=[proposal_obj.task.pk, proposal_obj.pk],
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == proposal_obj.pk


@pytest.mark.django_db
def test_proposal_retrieve_as_foreign_user_fail(api_client, proposal_obj):
    temp_user = User.objects.create_user(
        email="email@email.com", password="password", role=User.UserRole.CLIENT
    )
    api_client.force_authenticate(temp_user)
    response = api_client.get(
        reverse(
            "proposals:task-proposals-detail",
            args=[proposal_obj.task.pk, proposal_obj.pk],
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "id" not in response.data


# update


@pytest.mark.django_db
def test_proposal_update_not_found(api_client, freelancer_user):
    api_client.force_authenticate(freelancer_user)
    response = api_client.patch(
        reverse("proposals:task-proposals-detail", args=[0, 0]), {"message": "UPDATED"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "id" not in response.data


def test_proposal_update_unauthenticated(api_client, proposal_obj):
    response = api_client.patch(
        reverse(
            "proposals:task-proposals-detail",
            args=[proposal_obj.task.pk, proposal_obj.pk],
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
            "proposals:task-proposals-detail",
            args=[proposal_obj.task.pk, proposal_obj.pk],
        ),
        {"message": "UPDATED"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == proposal_obj.pk
    proposal_obj.refresh_from_db()
    assert proposal_obj.message == "UPDATED"


@pytest.mark.django_db
def test_proposal_update_as_foreign_user_fail(api_client, client_user, proposal_obj):
    api_client.force_authenticate(client_user)
    response = api_client.patch(
        reverse(
            "proposals:task-proposals-detail",
            args=[proposal_obj.task.pk, proposal_obj.pk],
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
            "proposals:task-proposals-detail",
            args=[proposal_obj.task.pk, proposal_obj.pk],
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
    response = api_client.delete(
        reverse("proposals:task-proposals-detail", args=[0, 0])
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_proposal_delete_unauthenticated(api_client, proposal_obj):
    response = api_client.delete(
        reverse(
            "proposals:task-proposals-detail",
            args=[proposal_obj.task.pk, proposal_obj.pk],
        )
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Proposal.objects.filter(pk=proposal_obj.pk).exists()


@pytest.mark.django_db
def test_proposal_delete_as_owner_success(api_client, freelancer_user, proposal_obj):
    api_client.force_authenticate(freelancer_user)
    response = api_client.delete(
        reverse(
            "proposals:task-proposals-detail",
            args=[proposal_obj.task.pk, proposal_obj.pk],
        )
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Proposal.objects.filter(pk=proposal_obj.pk).exists()


@pytest.mark.django_db
def test_proposal_delete_as_foreign_user_fail(api_client, client_user, proposal_obj):
    api_client.force_authenticate(client_user)
    response = api_client.delete(
        reverse(
            "proposals:task-proposals-detail",
            args=[proposal_obj.task.pk, proposal_obj.pk],
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Proposal.objects.filter(pk=proposal_obj.pk).exists()


@pytest.mark.django_db
def test_proposal_delete_is_not_pending_fail(api_client, client_user, proposal_obj):
    proposal_obj.status = Proposal.ProposalStatus.ACCEPTED
    proposal_obj.save()
    api_client.force_authenticate(client_user)
    response = api_client.delete(
        reverse(
            "proposals:task-proposals-detail",
            args=[proposal_obj.task.pk, proposal_obj.pk],
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Proposal.objects.filter(pk=proposal_obj.pk).exists()


# accept


@pytest.mark.django_db
def test_proposal_accept_as_proposal_task_owner_success(
    api_client, client_user, proposal_obj
):
    api_client.force_authenticate(client_user)
    response = api_client.post(
        reverse(
            "proposals:task-proposals-accept",
            args=[proposal_obj.task.pk, proposal_obj.pk],
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == proposal_obj.pk
    assert response.data.get("status") == Proposal.ProposalStatus.ACCEPTED
    proposal_obj.refresh_from_db()
    assert proposal_obj.status == Proposal.ProposalStatus.ACCEPTED
    assert proposal_obj.task.freelancer == proposal_obj.freelancer


@pytest.mark.django_db
def test_proposal_accept_as_foreign_user_fail(
    api_client, freelancer_user, proposal_obj
):
    api_client.force_authenticate(freelancer_user)
    response = api_client.post(
        reverse(
            "proposals:task-proposals-accept",
            args=[proposal_obj.task.pk, proposal_obj.pk],
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not "id" in response.data
    proposal_obj.refresh_from_db()
    assert proposal_obj.status != Proposal.ProposalStatus.ACCEPTED
    assert proposal_obj.task.freelancer != proposal_obj.freelancer


@pytest.mark.django_db
def test_proposal_accept_not_pending_proposal_fail(
    api_client, freelancer_user, proposal_obj
):
    proposal_obj.reject()
    api_client.force_authenticate(freelancer_user)
    response = api_client.post(
        reverse(
            "proposals:task-proposals-accept",
            args=[proposal_obj.task.pk, proposal_obj.pk],
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not "id" in response.data
    proposal_obj.refresh_from_db()
    assert proposal_obj.status != Proposal.ProposalStatus.ACCEPTED
    assert proposal_obj.task.freelancer != proposal_obj.freelancer


# reject


@pytest.mark.django_db
def test_proposal_reject_as_proposal_task_owner_success(
    api_client, client_user, proposal_obj
):
    api_client.force_authenticate(client_user)
    response = api_client.post(
        reverse(
            "proposals:task-proposals-reject",
            args=[proposal_obj.task.pk, proposal_obj.pk],
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == proposal_obj.pk
    assert response.data.get("status") == Proposal.ProposalStatus.REJECTED
    proposal_obj.refresh_from_db()
    assert proposal_obj.status == Proposal.ProposalStatus.REJECTED


@pytest.mark.django_db
def test_proposal_reject_as_foreign_user_fail(
    api_client, freelancer_user, proposal_obj
):
    api_client.force_authenticate(freelancer_user)
    response = api_client.post(
        reverse(
            "proposals:task-proposals-reject",
            args=[proposal_obj.task.pk, proposal_obj.pk],
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not "id" in response.data
    proposal_obj.refresh_from_db()
    assert proposal_obj.status != Proposal.ProposalStatus.REJECTED


@pytest.mark.django_db
def test_proposal_reject_not_pending_proposal_fail(
    api_client, freelancer_user, proposal_obj
):
    proposal_obj.accept()
    api_client.force_authenticate(freelancer_user)
    response = api_client.post(
        reverse(
            "proposals:task-proposals-reject",
            args=[proposal_obj.task.pk, proposal_obj.pk],
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not "id" in response.data
    proposal_obj.refresh_from_db()
    assert proposal_obj.status != Proposal.ProposalStatus.REJECTED

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


def test_proposal_list_unauthenticated(api_client, proposal_factory):
    proposal = proposal_factory()
    response = api_client.get(
        reverse("tasks:task-proposals-list", args=[proposal.task.pk])
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "results" not in response.data


@pytest.mark.django_db
def test_proposal_list_success(api_client, client_user, proposals):
    api_client.force_authenticate(client_user)
    response = api_client.get(
        reverse("tasks:task-proposals-list", args=[proposals[0].task.pk])
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("count") == len(proposals)
    assert "results" in response.data


@pytest.mark.django_db
def test_proposal_list_filter_by_status(api_client, client_user, proposals):
    api_client.force_authenticate(client_user)
    response = api_client.get(
        reverse("tasks:task-proposals-list", args=[proposals[0].task.pk]),
        {"status": Proposal.ProposalStatus.PENDING},
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data.get("results")) == 3
    for proposal_data in response.data.get("results"):
        assert proposal_data["status"] == Proposal.ProposalStatus.PENDING


@pytest.mark.django_db
def test_proposal_list_filter_by_freelancer(
    api_client, client_user, proposals, freelancer_user
):
    api_client.force_authenticate(client_user)
    response = api_client.get(
        reverse("tasks:task-proposals-list", args=[proposals[0].task.pk]),
        {"freelancer": freelancer_user.pk},
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data.get("results")) == 1
    for proposal_data in response.data.get("results"):
        assert proposal_data["freelancer"] == freelancer_user.pk


@pytest.mark.django_db
def test_proposal_list_search_by_message(api_client, client_user, proposals):
    api_client.force_authenticate(client_user)
    response = api_client.get(
        reverse("tasks:task-proposals-list", args=[proposals[0].task.pk]),
        {"search": "Pending proposal 1"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data.get("results")) == 1
    assert response.data.get("results")[0]["message"] == "Pending proposal 1"


@pytest.mark.django_db
def test_proposal_list_order_by_created_at_desc(api_client, client_user, proposals):
    api_client.force_authenticate(client_user)
    response = api_client.get(
        reverse("tasks:task-proposals-list", args=[proposals[0].task.pk]),
        {"ordering": "-created_at"},
    )

    assert response.status_code == status.HTTP_200_OK
    created_at_list = [
        proposal_data["created_at"] for proposal_data in response.data.get("results")
    ]
    assert created_at_list == sorted(created_at_list, reverse=True)


@pytest.mark.django_db
def test_proposal_list_order_by_created_at_asc(api_client, client_user, proposals):
    api_client.force_authenticate(client_user)
    response = api_client.get(
        reverse("tasks:task-proposals-list", args=[proposals[0].task.pk]),
        {"ordering": "created_at"},
    )

    assert response.status_code == status.HTTP_200_OK
    created_at_list = [
        proposal_data["created_at"] for proposal_data in response.data.get("results")
    ]
    assert created_at_list == sorted(created_at_list)


# create


def test_proposal_create_unauthenticated(api_client, task_factory, proposal_data):
    task = task_factory()
    response = api_client.post(
        reverse("tasks:task-proposals-list", args=[task.pk]), proposal_data
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not Proposal.objects.filter(message=proposal_data["message"]).exists()


@pytest.mark.django_db
def test_proposal_create_as_freelancer_success(
    api_client, freelancer_user, task_factory, proposal_data
):
    task = task_factory()
    api_client.force_authenticate(freelancer_user)
    response = api_client.post(
        reverse("tasks:task-proposals-list", args=[task.pk]), proposal_data
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert (
        Proposal.objects.get(message=proposal_data["message"]).freelancer
        == freelancer_user
    )


@pytest.mark.django_db
def test_proposal_create_already_exists_for_this_task_fail(
    api_client, freelancer_user, proposal_factory
):
    proposal = proposal_factory()
    api_client.force_authenticate(freelancer_user)
    response = api_client.post(
        reverse("tasks:task-proposals-list", args=[proposal.task.pk]),
        {"message": proposal.message},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Proposal.objects.filter(message=proposal.message).count() == 1


@pytest.mark.django_db
def test_proposal_create_as_client_fail(
    api_client, client_user, task_factory, proposal_data
):
    task = task_factory()
    api_client.force_authenticate(client_user)
    response = api_client.post(
        reverse("tasks:task-proposals-list", args=[task.pk]), proposal_data
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not Proposal.objects.filter(message=proposal_data["message"]).exists()


@pytest.mark.django_db
def test_proposal_create_task_is_not_open_fail(
    api_client, client_user, task_factory, proposal_data
):
    task = task_factory(status=Task.TaskStatus.IN_PROGRESS)
    api_client.force_authenticate(client_user)
    response = api_client.post(
        reverse("tasks:task-proposals-list", args=[task.pk]), proposal_data
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


def test_proposal_retrieve_unauthenticated(api_client, proposal_factory):
    proposal = proposal_factory()
    response = api_client.get(
        reverse("tasks:task-proposals-detail", args=[proposal.task.pk, proposal.pk])
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "id" not in response.data


@pytest.mark.django_db
def test_proposal_retrieve_as_proposal_task_owner_success(
    api_client, client_user, proposal_factory
):
    proposal = proposal_factory()
    api_client.force_authenticate(client_user)
    response = api_client.get(
        reverse("tasks:task-proposals-detail", args=[proposal.task.pk, proposal.pk])
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == proposal.pk


@pytest.mark.django_db
def test_proposal_retrieve_as_proposal_owner_success(
    api_client, freelancer_user, proposal_factory
):
    proposal = proposal_factory()
    api_client.force_authenticate(freelancer_user)
    response = api_client.get(
        reverse(
            "tasks:task-proposals-detail",
            args=[proposal.task.pk, proposal.pk],
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == proposal.pk


@pytest.mark.django_db
def test_proposal_retrieve_as_random_user_fail(
    api_client, random_user, proposal_factory
):
    proposal = proposal_factory()
    api_client.force_authenticate(random_user)
    response = api_client.get(
        reverse(
            "tasks:task-proposals-detail",
            args=[proposal.task.pk, proposal.pk],
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


def test_proposal_update_unauthenticated(api_client, proposal_factory):
    proposal = proposal_factory()
    response = api_client.patch(
        reverse(
            "tasks:task-proposals-detail",
            args=[proposal.task.pk, proposal.pk],
        ),
        {"message": "UPDATED"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "id" not in response.data
    proposal.refresh_from_db()
    assert proposal.message != "UPDATED"


@pytest.mark.django_db
def test_proposal_update_as_owner_success(
    api_client, freelancer_user, proposal_factory
):
    proposal = proposal_factory()
    api_client.force_authenticate(freelancer_user)
    response = api_client.patch(
        reverse(
            "tasks:task-proposals-detail",
            args=[proposal.task.pk, proposal.pk],
        ),
        {"message": "UPDATED"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == proposal.pk
    proposal.refresh_from_db()
    assert proposal.message == "UPDATED"


@pytest.mark.django_db
def test_proposal_update_as_random_user_fail(api_client, random_user, proposal_factory):
    proposal = proposal_factory()
    api_client.force_authenticate(random_user)
    response = api_client.patch(
        reverse(
            "tasks:task-proposals-detail",
            args=[proposal.task.pk, proposal.pk],
        ),
        {"message": "UPDATED"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "id" not in response.data
    proposal.refresh_from_db()
    assert proposal.message != "UPDATED"


@pytest.mark.django_db
def test_proposal_update_status_is_not_pending_fail(
    api_client, freelancer_user, proposal_factory
):
    proposal = proposal_factory(status=Proposal.ProposalStatus.ACCEPTED)
    api_client.force_authenticate(freelancer_user)
    response = api_client.patch(
        reverse(
            "tasks:task-proposals-detail",
            args=[proposal.task.pk, proposal.pk],
        ),
        {"message": "UPDATED"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "id" not in response.data
    proposal.refresh_from_db()
    assert proposal.message != "UPDATED"


# delete


@pytest.mark.django_db
def test_proposal_delete_not_found(api_client, freelancer_user):
    api_client.force_authenticate(freelancer_user)
    response = api_client.delete(reverse("tasks:task-proposals-detail", args=[0, 0]))

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_proposal_delete_unauthenticated(api_client, proposal_factory):
    proposal = proposal_factory()
    response = api_client.delete(
        reverse(
            "tasks:task-proposals-detail",
            args=[proposal.task.pk, proposal.pk],
        )
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Proposal.objects.filter(pk=proposal.pk).exists()


@pytest.mark.django_db
def test_proposal_delete_as_owner_success(
    api_client, freelancer_user, proposal_factory
):
    proposal = proposal_factory()
    api_client.force_authenticate(freelancer_user)
    response = api_client.delete(
        reverse(
            "tasks:task-proposals-detail",
            args=[proposal.task.pk, proposal.pk],
        )
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Proposal.objects.filter(pk=proposal.pk).exists()


@pytest.mark.django_db
def test_proposal_delete_as_random_user_fail(api_client, random_user, proposal_factory):
    proposal = proposal_factory()
    api_client.force_authenticate(random_user)
    response = api_client.delete(
        reverse(
            "tasks:task-proposals-detail",
            args=[proposal.task.pk, proposal.pk],
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Proposal.objects.filter(pk=proposal.pk).exists()


@pytest.mark.django_db
def test_proposal_delete_is_not_pending_fail(api_client, client_user, proposal_factory):
    proposal = proposal_factory(status=Proposal.ProposalStatus.ACCEPTED)
    api_client.force_authenticate(client_user)
    response = api_client.delete(
        reverse(
            "tasks:task-proposals-detail",
            args=[proposal.task.pk, proposal.pk],
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Proposal.objects.filter(pk=proposal.pk).exists()


# accept


@pytest.mark.django_db
def test_proposal_accept_as_proposal_task_owner_success(
    api_client, client_user, proposal_factory
):
    proposal = proposal_factory()
    api_client.force_authenticate(client_user)
    response = api_client.post(
        reverse(
            "tasks:task-proposals-accept",
            args=[proposal.task.pk, proposal.pk],
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == proposal.pk
    assert response.data.get("status") == Proposal.ProposalStatus.ACCEPTED
    proposal.refresh_from_db()
    assert proposal.status == Proposal.ProposalStatus.ACCEPTED
    assert proposal.task.freelancer == proposal.freelancer


@pytest.mark.django_db
def test_proposal_accept_as_random_user_fail(api_client, random_user, proposal_factory):
    proposal = proposal_factory()
    api_client.force_authenticate(random_user)
    response = api_client.post(
        reverse(
            "tasks:task-proposals-accept",
            args=[proposal.task.pk, proposal.pk],
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "id" not in response.data
    proposal.refresh_from_db()
    assert proposal.status != Proposal.ProposalStatus.ACCEPTED
    assert proposal.task.freelancer != proposal.freelancer


@pytest.mark.django_db
def test_proposal_accept_not_pending_proposal_fail(
    api_client, freelancer_user, proposal_factory
):
    proposal = proposal_factory(status=Proposal.ProposalStatus.REJECTED)
    api_client.force_authenticate(freelancer_user)
    response = api_client.post(
        reverse(
            "tasks:task-proposals-accept",
            args=[proposal.task.pk, proposal.pk],
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "id" not in response.data
    proposal.refresh_from_db()
    assert proposal.status != Proposal.ProposalStatus.ACCEPTED
    assert proposal.task.freelancer != proposal.freelancer


# reject


@pytest.mark.django_db
def test_proposal_reject_as_proposal_task_owner_success(
    api_client, client_user, proposal_factory
):
    proposal = proposal_factory()
    api_client.force_authenticate(client_user)
    response = api_client.post(
        reverse(
            "tasks:task-proposals-reject",
            args=[proposal.task.pk, proposal.pk],
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == proposal.pk
    assert response.data.get("status") == Proposal.ProposalStatus.REJECTED
    proposal.refresh_from_db()
    assert proposal.status == Proposal.ProposalStatus.REJECTED


@pytest.mark.django_db
def test_proposal_reject_as_random_user_fail(api_client, random_user, proposal_factory):
    proposal = proposal_factory()
    api_client.force_authenticate(random_user)
    response = api_client.post(
        reverse(
            "tasks:task-proposals-reject",
            args=[proposal.task.pk, proposal.pk],
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "id" not in response.data
    proposal.refresh_from_db()
    assert proposal.status != Proposal.ProposalStatus.REJECTED


@pytest.mark.django_db
def test_proposal_reject_not_pending_proposal_fail(
    api_client, client_user, proposal_factory
):
    proposal = proposal_factory(status=Proposal.ProposalStatus.ACCEPTED)
    api_client.force_authenticate(client_user)
    response = api_client.post(
        reverse(
            "tasks:task-proposals-reject",
            args=[proposal.task.pk, proposal.pk],
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "id" not in response.data
    proposal.refresh_from_db()
    assert proposal.status != Proposal.ProposalStatus.REJECTED

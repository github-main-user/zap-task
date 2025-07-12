import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

User = get_user_model()


# token obtain pair


@pytest.mark.django_db
def test_obtain_token_pair_success(api_client, client_user):
    response = api_client.post(
        reverse("users:token_obtain_pair"),
        {"email": "client@client.com", "password": "pass"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_obtain_token_pair_wrong_credentials(api_client):
    response = api_client.post(
        reverse("users:token_obtain_pair"),
        {"email": "wrong@wrong.com", "password": "wrong"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "access" not in response.data
    assert "refresh" not in response.data


# refresh token


@pytest.mark.django_db
def test_refresh_token_success(api_client, client_user):
    response = api_client.post(
        reverse("users:token_obtain_pair"),
        {"email": "client@client.com", "password": "pass"},
    )
    assert response.status_code == status.HTTP_200_OK

    refresh_token = response.data.get("refresh")
    response = api_client.post(
        reverse("users:token_refresh"), {"refresh": refresh_token}
    )

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data


@pytest.mark.django_db
def test_refresh_token_invalid(api_client):
    response = api_client.post(reverse("users:token_refresh"), {"refresh": "WRONG"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "access" not in response.data


# registration


@pytest.mark.django_db
def client_user_register_success(api_client):
    response = api_client.post(
        reverse("users:register"), {"email": "new@user.com", "password": "pass"}
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(email="new@user.com").exists()


@pytest.mark.django_db
def client_user_register_already_exists(api_client, client_user):
    response = api_client.post(
        reverse("users:register"), {"email": "client@client.com", "password": "pass"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not User.objects.filter(email="new@user.com").exists()


# me/ retrieve


def test_retrieve_me_unauthenticated(api_client):
    response = api_client.get(reverse("users:user-me"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_retrieve_me_success(api_client, client_user):
    api_client.force_authenticate(client_user)
    response = api_client.get(reverse("users:user-me"))

    assert response.status_code == status.HTTP_200_OK
    assert client_user.email == response.data.get("email")


# me/ update


def test_update_me_unauthenticated(api_client, client_user):
    response = api_client.patch(reverse("users:user-me"), {"first_name": "UPDATED"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    client_user.refresh_from_db()
    assert client_user.first_name != "UPDATED"


@pytest.mark.django_db
def test_update_me_success(api_client, client_user):
    api_client.force_authenticate(client_user)
    response = api_client.patch(reverse("users:user-me"), {"first_name": "UPDATED"})

    assert response.status_code == status.HTTP_200_OK
    client_user.refresh_from_db()
    assert client_user.first_name == "UPDATED"


# me/ delete


def test_delete_me_unauthenticated(api_client, client_user):
    response = api_client.delete(reverse("users:user-me"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert User.objects.filter(email=client_user.email).exists()


@pytest.mark.django_db
def test_delete_me_success(api_client, client_user):
    api_client.force_authenticate(client_user)
    response = api_client.delete(reverse("users:user-me"))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not User.objects.filter(email=client_user.email).exists()


# user public detail


def test_retrieve_user_unauthenticated(api_client, client_user):
    response = api_client.get(
        reverse("users:user-public-detail", args=[client_user.pk])
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "id" not in response.data


@pytest.mark.django_db
def test_retrieve_user_success(api_client, client_user, freelancer_user):
    api_client.force_authenticate(client_user)
    response = api_client.get(
        reverse("users:user-public-detail", args=[freelancer_user.pk])
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("id") == freelancer_user.pk


# change password


def test_change_password_unauthenticated(api_client):
    response = api_client.put(
        reverse("users:change-password"),
        {"old_password": "pass", "new_password": "new_pass"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_change_password_success(api_client, client_user):
    api_client.force_authenticate(client_user)
    response = api_client.put(
        reverse("users:change-password"),
        {"old_password": "pass", "new_password": "new_pass"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    client_user.refresh_from_db()
    assert client_user.check_password("new_pass")


@pytest.mark.django_db
def test_change_password_wrong_old_password(api_client, client_user):
    api_client.force_authenticate(client_user)
    response = api_client.put(
        reverse("users:change-password"),
        {"old_password": "wrong_pass", "new_password": "new_pass"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    client_user.refresh_from_db()
    assert not client_user.check_password("new_pass")

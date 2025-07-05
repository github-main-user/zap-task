import pytest
from django.urls import reverse
from rest_framework import status


@pytest.fixture
def test_user(django_user_model):
    return django_user_model.objects.create_user("test@test.com", "pass")


# token obtain pair


@pytest.mark.django_db
def test_obtain_token_pair_success(api_client, test_user):
    response = api_client.post(
        reverse("users:token_obtain_pair"),
        {"email": "test@test.com", "password": "pass"},
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
def test_refresh_token_success(api_client, test_user):
    response = api_client.post(
        reverse("users:token_obtain_pair"),
        {"email": "test@test.com", "password": "pass"},
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
def test_user_register_success(api_client, django_user_model):
    response = api_client.post(
        reverse("users:register"), {"email": "new@user.com", "password": "pass"}
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert django_user_model.objects.filter(email="new@user.com").exists()


@pytest.mark.django_db
def test_user_register_already_exists(api_client, django_user_model, test_user):
    response = api_client.post(
        reverse("users:register"), {"email": "test@test.com", "password": "pass"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not django_user_model.objects.filter(email="new@user.com").exists()


# me/ retrieve


@pytest.mark.django_db
def test_retrieve_me_unauthenticated(api_client):
    response = api_client.get(reverse("users:me"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_retrieve_me_success(api_client, test_user):
    api_client.force_authenticate(test_user)
    response = api_client.get(reverse("users:me"))

    assert response.status_code == status.HTTP_200_OK
    assert test_user.email == response.data.get("email")


# me/ update


@pytest.mark.django_db
def test_update_me_unauthenticated(api_client, test_user):
    response = api_client.patch(reverse("users:me"), {"first_name": "UPDATED"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    test_user.refresh_from_db()
    assert test_user.first_name != "UPDATED"


@pytest.mark.django_db
def test_update_me_success(api_client, test_user):
    api_client.force_authenticate(test_user)
    response = api_client.patch(reverse("users:me"), {"first_name": "UPDATED"})

    assert response.status_code == status.HTTP_200_OK
    test_user.refresh_from_db()
    assert test_user.first_name == "UPDATED"


# me/ delete


@pytest.mark.django_db
def test_delete_me_unauthenticated(api_client, django_user_model, test_user):
    response = api_client.delete(reverse("users:me"))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert django_user_model.objects.filter(email=test_user.email).exists()


@pytest.mark.django_db
def test_delete_me_success(api_client, django_user_model, test_user):
    api_client.force_authenticate(test_user)
    response = api_client.delete(reverse("users:me"))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not django_user_model.objects.filter(email=test_user.email).exists()

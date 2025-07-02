import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_create_user_success():
    user = User.objects.create_user(email="test@example.com", password="testpass123")

    assert user.email == "test@example.com"
    assert user.check_password("testpass123")
    assert not user.is_staff
    assert not user.is_superuser


@pytest.mark.django_db
def test_create_user_without_email_raises_error():
    with pytest.raises(ValueError):
        User.objects.create_user(email=None, password="testpass123")


@pytest.mark.django_db
def test_create_superuser_success():
    admin = User.objects.create_superuser(
        email="admin@example.com", password="adminpass"
    )

    assert admin.is_staff
    assert admin.is_superuser


@pytest.mark.django_db
def test_create_superuser_with_wrong_flags_raises_error():
    with pytest.raises(ValueError):
        User.objects.create_superuser(
            email="badadmin@example.com", password="adminpass", is_staff=False
        )

    with pytest.raises(ValueError):
        User.objects.create_superuser(
            email="badadmin2@example.com", password="adminpass", is_superuser=False
        )

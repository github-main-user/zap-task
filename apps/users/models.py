from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import TimeStampModel

from .managers import UserManager


class User(AbstractUser, TimeStampModel):
    class UserRoles(models.TextChoices):
        CLIENT = "client", "Client"
        FREELANCER = "freelancer", "Freelancer"

    username = None
    date_joined = None

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=UserRoles)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: UserManager = UserManager()

    def __str__(self) -> str:
        return self.email

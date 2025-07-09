from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import TimeStampModel

from .managers import UserManager


class User(AbstractUser, TimeStampModel):
    class UserRole(models.TextChoices):
        CLIENT = "client", "Client"
        FREELANCER = "freelancer", "Freelancer"

    username = None
    date_joined = None

    email = models.EmailField(unique=True, help_text="Email address of the user.")
    role = models.CharField(
        max_length=10,
        choices=UserRole.choices,
        default=UserRole.CLIENT,
        help_text="Role of the user.",
    )
    average_rating = models.FloatField(
        default=0.0, help_text="Average rating of the user."
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: UserManager = UserManager()

    class Meta:
        indexes = [models.Index(fields=["role"])]

    def __str__(self) -> str:
        return self.email

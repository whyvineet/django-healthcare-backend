from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts.managers import UserManager


class User(AbstractUser):
    username = None

    email = models.EmailField(
        unique=True,
        verbose_name="email address",
    )

    name = models.CharField(
        max_length=255,
        verbose_name="full name",
    )

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.email

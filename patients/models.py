from django.conf import settings
from django.db import models


class Patient(models.Model):

    name = models.CharField(max_length=255, verbose_name="full name")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="date of birth")
    phone = models.CharField(max_length=20, blank=True, verbose_name="contact phone")
    address = models.TextField(blank=True, verbose_name="address")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patients",
        verbose_name="created by",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} (owner: {self.created_by_id})"

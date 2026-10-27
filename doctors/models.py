from django.conf import settings
from django.db import models


class Doctor(models.Model):
    name = models.CharField(max_length=255, verbose_name="full name")
    specialization = models.CharField(max_length=255, verbose_name="specialization")
    email = models.EmailField(blank=True, verbose_name="email address")
    phone = models.CharField(max_length=20, blank=True, verbose_name="contact phone")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="doctors_created",
        verbose_name="created by",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"Dr. {self.name} ({self.specialization})"

from django.conf import settings
from django.db import models

from doctors.models import Doctor
from patients.models import Patient


class PatientDoctorMapping(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="mappings",
        verbose_name="patient",
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="mappings",
        verbose_name="doctor",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assignments_made",
        verbose_name="assigned by",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["patient", "doctor"],
                name="unique_patient_doctor",
            )
        ]

    def __str__(self):
        return f"Patient {self.patient_id} ↔ Doctor {self.doctor_id}"

from django.db import IntegrityError
from rest_framework import serializers

from mappings.models import PatientDoctorMapping
from patients.models import Patient
from doctors.models import Doctor


class MappingSerializer(serializers.ModelSerializer):

    class Meta:
        model = PatientDoctorMapping
        fields = (
            "id",
            "patient",
            "doctor",
            "assigned_by",
            "created_at",
        )
        read_only_fields = ("id", "assigned_by", "created_at")

    def validate(self, attrs):
        patient = attrs.get("patient")
        doctor = attrs.get("doctor")
        if patient and doctor:
            if PatientDoctorMapping.objects.filter(
                patient=patient, doctor=doctor
            ).exists():
                raise serializers.ValidationError(
                    "This doctor is already assigned to the selected patient."
                )
        return attrs

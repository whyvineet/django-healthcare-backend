from django.db import IntegrityError
from rest_framework import serializers

from doctors.models import Doctor
from doctors.serializers import DoctorSerializer
from mappings.models import PatientDoctorMapping
from patients.models import Patient


class MappingSerializer(serializers.ModelSerializer):
    doctor_details = DoctorSerializer(source="doctor", read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = (
            "id",
            "patient",
            "doctor",
            "doctor_details",
            "assigned_by",
            "created_at",
        )
        read_only_fields = ("id", "assigned_by", "created_at", "doctor_details")

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

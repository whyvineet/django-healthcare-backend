from rest_framework import serializers

from patients.models import Patient


class PatientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Patient
        fields = (
            "id",
            "name",
            "date_of_birth",
            "phone",
            "address",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "created_at", "updated_at")

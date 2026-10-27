from rest_framework import serializers

from doctors.models import Doctor


class DoctorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Doctor
        fields = (
            "id",
            "name",
            "specialization",
            "email",
            "phone",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "created_at", "updated_at")

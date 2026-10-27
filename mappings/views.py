from django.db import IntegrityError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from mappings.models import PatientDoctorMapping
from mappings.serializers import MappingSerializer
from patients.models import Patient


class MappingListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        mappings = PatientDoctorMapping.objects.filter(
            patient__created_by=request.user
        ).select_related("patient", "doctor", "assigned_by")
        serializer = MappingSerializer(mappings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = MappingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        patient = serializer.validated_data.get("patient")

        if patient.created_by != request.user:
            return Response(
                {"detail": "You do not have permission to assign a doctor to this patient."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            mapping = serializer.save(assigned_by=request.user)
        except IntegrityError:
            return Response(
                {"detail": "This doctor is already assigned to the selected patient."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            MappingSerializer(mapping).data, status=status.HTTP_201_CREATED
        )


class MappingDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        patient = Patient.objects.filter(
            pk=pk, created_by=request.user
        ).first()
        if patient is None:
            return Response(
                {"detail": "Patient not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        mappings = PatientDoctorMapping.objects.filter(
            patient=patient
        ).select_related("patient", "doctor", "assigned_by")
        serializer = MappingSerializer(mappings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        mapping = PatientDoctorMapping.objects.filter(
            pk=pk, patient__created_by=request.user
        ).first()
        if mapping is None:
            return Response(
                {"detail": "Mapping not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

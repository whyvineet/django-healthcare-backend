from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from doctors.models import Doctor
from doctors.permissions import IsDoctorCreatorOrReadOnly
from doctors.serializers import DoctorSerializer


class DoctorViewSet(viewsets.ModelViewSet):

    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, IsDoctorCreatorOrReadOnly]

    def get_queryset(self):
        return Doctor.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

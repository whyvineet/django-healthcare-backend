from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from doctors.models import Doctor

User = get_user_model()

DOCTORS_URL = "/api/doctors/"


def doctors_detail_url(pk):
    return f"/api/doctors/{pk}/"


def get_token(user):
    return str(RefreshToken.for_user(user).access_token)


class DoctorTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="doc_tester@example.com", name="Tester", password="pass"
        )
        self.other_user = User.objects.create_user(
            email="other@example.com", name="Other", password="pass"
        )

    def auth(self, user=None):
        if user is None:
            user = self.user
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {get_token(user)}")

    def test_create_doctor_success(self):
        self.auth()
        payload = {"name": "Dr. Smith", "specialization": "Cardiology"}
        response = self.client.post(DOCTORS_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Dr. Smith")
        self.assertEqual(response.data["specialization"], "Cardiology")
        self.assertEqual(response.data["created_by"], self.user.pk)

    def test_create_doctor_requires_name_and_specialization(self):
        self.auth()
        response = self.client.post(DOCTORS_URL, {"specialization": "Surgery"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post(DOCTORS_URL, {"name": "Dr. X"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_doctor_unauthenticated(self):
        response = self.client.post(
            DOCTORS_URL, {"name": "Dr. Y", "specialization": "GP"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_doctors_shared_directory(self):
        Doctor.objects.create(name="Dr. Alpha", specialization="Neurology", created_by=self.user)
        Doctor.objects.create(name="Dr. Beta", specialization="Dermatology", created_by=self.other_user)
        self.auth()
        response = self.client.get(DOCTORS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [d["name"] for d in response.data]
        self.assertIn("Dr. Alpha", names)
        self.assertIn("Dr. Beta", names)

    def test_list_requires_auth(self):
        response = self.client.get(DOCTORS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_doctor(self):
        doctor = Doctor.objects.create(name="Dr. Gamma", specialization="GP", created_by=self.user)
        self.auth()
        response = self.client.get(doctors_detail_url(doctor.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Dr. Gamma")

    def test_retrieve_nonexistent_doctor_returns_404(self):
        self.auth()
        response = self.client.get(doctors_detail_url(99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_doctor(self):
        doctor = Doctor.objects.create(name="Dr. Old", specialization="Surgery", created_by=self.user)
        self.auth()
        response = self.client.put(
            doctors_detail_url(doctor.pk),
            {"name": "Dr. New", "specialization": "Orthopedics"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Dr. New")

    def test_delete_doctor(self):
        doctor = Doctor.objects.create(name="Dr. Delete", specialization="GP", created_by=self.user)
        self.auth()
        response = self.client.delete(doctors_detail_url(doctor.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Doctor.objects.filter(pk=doctor.pk).exists())

    def test_delete_nonexistent_doctor_returns_404(self):
        self.auth()
        response = self.client.delete(doctors_detail_url(99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from patients.models import Patient

User = get_user_model()

PATIENTS_URL = "/api/patients/"


def patients_detail_url(pk):
    return f"/api/patients/{pk}/"


def get_token(user):
    return str(RefreshToken.for_user(user).access_token)


class PatientTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_a = User.objects.create_user(
            email="usera@example.com", name="User A", password="pass"
        )
        self.user_b = User.objects.create_user(
            email="userb@example.com", name="User B", password="pass"
        )

    def auth(self, user):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {get_token(user)}")

    def test_create_patient_success(self):
        self.auth(self.user_a)
        payload = {"name": "John Doe", "phone": "555-0100"}
        response = self.client.post(PATIENTS_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "John Doe")
        self.assertEqual(response.data["created_by"], self.user_a.pk)

    def test_create_patient_requires_auth(self):
        response = self.client.post(PATIENTS_URL, {"name": "Jane"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_patient_missing_name_returns_400(self):
        self.auth(self.user_a)
        response = self.client.post(PATIENTS_URL, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_client_cannot_set_owner(self):
        self.auth(self.user_a)
        payload = {"name": "Patient X", "created_by": self.user_b.pk}
        response = self.client.post(PATIENTS_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["created_by"], self.user_a.pk)

    def test_list_returns_only_own_patients(self):
        Patient.objects.create(name="A1", created_by=self.user_a)
        Patient.objects.create(name="A2", created_by=self.user_a)
        Patient.objects.create(name="B1", created_by=self.user_b)

        self.auth(self.user_a)
        response = self.client.get(PATIENTS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [p["name"] for p in response.data]
        self.assertIn("A1", names)
        self.assertIn("A2", names)
        self.assertNotIn("B1", names)

    def test_retrieve_owned_patient(self):
        patient = Patient.objects.create(name="My Patient", created_by=self.user_a)
        self.auth(self.user_a)
        response = self.client.get(patients_detail_url(patient.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "My Patient")

    def test_user_b_cannot_retrieve_user_a_patient(self):
        patient = Patient.objects.create(name="Private", created_by=self.user_a)
        self.auth(self.user_b)
        response = self.client.get(patients_detail_url(patient.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_owned_patient(self):
        patient = Patient.objects.create(name="Old Name", created_by=self.user_a)
        self.auth(self.user_a)
        response = self.client.put(
            patients_detail_url(patient.pk),
            {"name": "New Name"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "New Name")

    def test_user_b_cannot_update_user_a_patient(self):
        patient = Patient.objects.create(name="Original", created_by=self.user_a)
        self.auth(self.user_b)
        response = self.client.put(
            patients_detail_url(patient.pk),
            {"name": "Hacked"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_owned_patient(self):
        patient = Patient.objects.create(name="To Delete", created_by=self.user_a)
        self.auth(self.user_a)
        response = self.client.delete(patients_detail_url(patient.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Patient.objects.filter(pk=patient.pk).exists())

    def test_user_b_cannot_delete_user_a_patient(self):
        patient = Patient.objects.create(name="Protected", created_by=self.user_a)
        self.auth(self.user_b)
        response = self.client.delete(patients_detail_url(patient.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Patient.objects.filter(pk=patient.pk).exists())

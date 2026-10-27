from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from doctors.models import Doctor
from mappings.models import PatientDoctorMapping
from patients.models import Patient

User = get_user_model()

MAPPINGS_URL = "/api/mappings/"


def mapping_detail_url(pk):
    return f"/api/mappings/{pk}/"


def get_token(user):
    return str(RefreshToken.for_user(user).access_token)


class MappingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_a = User.objects.create_user(
            email="mappinga@example.com", name="User A", password="pass"
        )
        self.user_b = User.objects.create_user(
            email="mappingb@example.com", name="User B", password="pass"
        )
        self.patient_a = Patient.objects.create(name="Patient A", created_by=self.user_a)
        self.patient_b = Patient.objects.create(name="Patient B", created_by=self.user_b)
        self.doctor = Doctor.objects.create(
            name="Dr. House", specialization="Diagnostics", created_by=self.user_a
        )
        self.doctor2 = Doctor.objects.create(
            name="Dr. Wilson", specialization="Oncology", created_by=self.user_a
        )

    def auth(self, user):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {get_token(user)}")


    def test_assign_doctor_to_owned_patient(self):
        self.auth(self.user_a)
        payload = {"patient": self.patient_a.pk, "doctor": self.doctor.pk}
        response = self.client.post(MAPPINGS_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["patient"], self.patient_a.pk)
        self.assertEqual(response.data["doctor"], self.doctor.pk)
        self.assertEqual(response.data["assigned_by"], self.user_a.pk)

    def test_assign_to_another_users_patient_forbidden(self):
        self.auth(self.user_a)
        payload = {"patient": self.patient_b.pk, "doctor": self.doctor.pk}
        response = self.client.post(MAPPINGS_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_assign_nonexistent_patient_returns_400(self):
        self.auth(self.user_a)
        payload = {"patient": 99999, "doctor": self.doctor.pk}
        response = self.client.post(MAPPINGS_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_nonexistent_doctor_returns_400(self):
        self.auth(self.user_a)
        payload = {"patient": self.patient_a.pk, "doctor": 99999}
        response = self.client.post(MAPPINGS_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_assignment_returns_400(self):
        PatientDoctorMapping.objects.create(
            patient=self.patient_a, doctor=self.doctor, assigned_by=self.user_a
        )
        self.auth(self.user_a)
        payload = {"patient": self.patient_a.pk, "doctor": self.doctor.pk}
        response = self.client.post(MAPPINGS_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_mapping_requires_auth(self):
        payload = {"patient": self.patient_a.pk, "doctor": self.doctor.pk}
        response = self.client.post(MAPPINGS_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_mappings_for_own_patients_only(self):
        PatientDoctorMapping.objects.create(
            patient=self.patient_a, doctor=self.doctor, assigned_by=self.user_a
        )
        PatientDoctorMapping.objects.create(
            patient=self.patient_b, doctor=self.doctor2, assigned_by=self.user_b
        )
        self.auth(self.user_a)
        response = self.client.get(MAPPINGS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        patient_ids = [m["patient"] for m in response.data]
        self.assertIn(self.patient_a.pk, patient_ids)
        self.assertNotIn(self.patient_b.pk, patient_ids)

    def test_get_doctors_for_patient(self):
        PatientDoctorMapping.objects.create(
            patient=self.patient_a, doctor=self.doctor, assigned_by=self.user_a
        )
        PatientDoctorMapping.objects.create(
            patient=self.patient_a, doctor=self.doctor2, assigned_by=self.user_a
        )
        self.auth(self.user_a)
        response = self.client.get(mapping_detail_url(self.patient_a.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        doctor_ids = [m["doctor"] for m in response.data]
        self.assertIn(self.doctor.pk, doctor_ids)
        self.assertIn(self.doctor2.pk, doctor_ids)

    def test_get_doctors_for_another_users_patient_returns_404(self):
        PatientDoctorMapping.objects.create(
            patient=self.patient_b, doctor=self.doctor, assigned_by=self.user_b
        )
        self.auth(self.user_a)
        response = self.client.get(mapping_detail_url(self.patient_b.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_identifier_is_patient_id_not_mapping_id(self):
        mapping = PatientDoctorMapping.objects.create(
            patient=self.patient_a, doctor=self.doctor, assigned_by=self.user_a
        )
        self.auth(self.user_a)
        response = self.client.get(mapping_detail_url(self.patient_a.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], mapping.pk)


    def test_delete_mapping_by_mapping_id(self):
        mapping = PatientDoctorMapping.objects.create(
            patient=self.patient_a, doctor=self.doctor, assigned_by=self.user_a
        )
        self.auth(self.user_a)
        response = self.client.delete(mapping_detail_url(mapping.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(PatientDoctorMapping.objects.filter(pk=mapping.pk).exists())

    def test_delete_mapping_does_not_delete_patient_or_doctor(self):
        mapping = PatientDoctorMapping.objects.create(
            patient=self.patient_a, doctor=self.doctor, assigned_by=self.user_a
        )
        self.auth(self.user_a)
        self.client.delete(mapping_detail_url(mapping.pk))
        self.assertTrue(Patient.objects.filter(pk=self.patient_a.pk).exists())
        self.assertTrue(Doctor.objects.filter(pk=self.doctor.pk).exists())

    def test_delete_another_users_mapping_returns_404(self):
        mapping = PatientDoctorMapping.objects.create(
            patient=self.patient_b, doctor=self.doctor, assigned_by=self.user_b
        )
        self.auth(self.user_a)
        response = self.client.delete(mapping_detail_url(mapping.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(PatientDoctorMapping.objects.filter(pk=mapping.pk).exists())

    def test_delete_identifier_is_mapping_id(self):
        mapping = PatientDoctorMapping.objects.create(
            patient=self.patient_a, doctor=self.doctor, assigned_by=self.user_a
        )
        self.auth(self.user_a)
        response = self.client.delete(mapping_detail_url(mapping.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

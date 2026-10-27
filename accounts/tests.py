from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()

REGISTER_URL = "/api/auth/register/"
LOGIN_URL = "/api/auth/login/"
REFRESH_URL = "/api/auth/token/refresh/"
PROTECTED_URL = "/api/patients/"


class RegistrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_success(self):
        payload = {"name": "Alice", "email": "alice@example.com", "password": "StrongPass123!"}
        response = self.client.post(REGISTER_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], "alice@example.com")
        self.assertEqual(response.data["user"]["name"], "Alice")
        self.assertNotIn("password", response.data)
        self.assertNotIn("password", response.data.get("user", {}))

    def test_register_missing_name(self):
        payload = {"email": "bob@example.com", "password": "StrongPass123!"}
        response = self.client.post(REGISTER_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_email(self):
        payload = {"name": "Bob", "password": "StrongPass123!"}
        response = self.client.post(REGISTER_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_password(self):
        payload = {"name": "Bob", "email": "bob@example.com"}
        response = self.client.post(REGISTER_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_email_format(self):
        payload = {"name": "Bob", "email": "not-an-email", "password": "StrongPass123!"}
        response = self.client.post(REGISTER_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(self):
        User.objects.create_user(
            email="duplicate@example.com", name="First", password="StrongPass123!"
        )
        payload = {"name": "Second", "email": "duplicate@example.com", "password": "StrongPass123!"}
        response = self.client.post(REGISTER_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email_case_insensitive(self):
        User.objects.create_user(
            email="alice@example.com", name="Alice", password="StrongPass123!"
        )
        payload = {"name": "Alice 2", "email": "ALICE@EXAMPLE.COM", "password": "StrongPass123!"}
        response = self.client.post(REGISTER_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        payload_mixed = {"name": "Alice 3", "email": "AliCe@Example.Com", "password": "StrongPass123!"}
        response_mixed = self.client.post(REGISTER_URL, payload_mixed, format="json")
        self.assertEqual(response_mixed.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_is_hashed(self):
        payload = {"name": "Carol", "email": "carol@example.com", "password": "StrongPass123!"}
        self.client.post(REGISTER_URL, payload, format="json")
        user = User.objects.get(email="carol@example.com")
        self.assertNotEqual(user.password, "StrongPass123!")
        self.assertTrue(user.check_password("StrongPass123!"))


class LoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="dave@example.com", name="Dave", password="StrongPass123!"
        )

    def test_login_success(self):
        payload = {"email": "dave@example.com", "password": "StrongPass123!"}
        response = self.client.post(LOGIN_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_case_insensitive(self):
        payload = {"email": "DAVE@EXAMPLE.COM", "password": "StrongPass123!"}
        response = self.client.post(LOGIN_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_login_mixed_case(self):
        payload = {"email": "DaVe@Example.Com", "password": "StrongPass123!"}
        response = self.client.post(LOGIN_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_login_invalid_password(self):
        payload = {"email": "dave@example.com", "password": "WrongPassword"}
        response = self.client.post(LOGIN_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_email(self):
        payload = {"email": "nobody@example.com", "password": "StrongPass123!"}
        response = self.client.post(LOGIN_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_requires_token(self):
        response = self.client.get(PROTECTED_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_with_valid_token(self):
        login_response = self.client.post(
            LOGIN_URL, {"email": "dave@example.com", "password": "StrongPass123!"}, format="json"
        )
        token = login_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(PROTECTED_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_token_refresh(self):
        login_response = self.client.post(
            LOGIN_URL, {"email": "dave@example.com", "password": "StrongPass123!"}, format="json"
        )
        refresh_token = login_response.data["refresh"]
        response = self.client.post(REFRESH_URL, {"refresh": refresh_token}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

from django.db import IntegrityError
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import RegisterSerializer, is_duplicate_email_error


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
            except serializers.ValidationError as exc:
                return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
            except IntegrityError as exc:
                if is_duplicate_email_error(exc, request.data.get("email")):
                    return Response(
                        {"email": ["A user with this email already exists."]},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                raise
            return Response(
                {
                    "message": "User registered successfully.",
                    "user": {
                        "id": user.pk,
                        "name": user.name,
                        "email": user.email,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

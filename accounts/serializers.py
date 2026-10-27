from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError, transaction
from rest_framework import serializers

User = get_user_model()


def is_duplicate_email_error(exc, email=None):
    exc_str = str(exc).lower()

    cause = getattr(exc, "__cause__", None)
    pgcode = getattr(cause, "pgcode", None)
    is_unique_violation = (
        pgcode == "23505"
        or "unique" in exc_str
        or "duplicate" in exc_str
        or "already exists" in exc_str
    )

    mentions_email = "email" in exc_str or "unique_lower_email" in exc_str

    if is_unique_violation and mentions_email:
        return True

    if email:
        normalized = User.objects.normalize_email(email)
        if normalized and User.objects.filter(email__iexact=normalized).exists():
            if is_unique_violation or not exc_str or mentions_email:
                return True

    return False


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ("name", "email", "password")
        extra_kwargs = {
            "email": {
                "validators": [],
            }
        }

    def validate_email(self, value):
        normalized = User.objects.normalize_email(value)
        if User.objects.filter(email__iexact=normalized).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return normalized

    def create(self, validated_data):
        email = validated_data["email"]
        try:
            with transaction.atomic():
                return User.objects.create_user(
                    email=email,
                    name=validated_data["name"].strip(),
                    password=validated_data["password"],
                )
        except IntegrityError as exc:
            if is_duplicate_email_error(exc, email):
                raise serializers.ValidationError(
                    {"email": ["A user with this email already exists."]}
                )
            raise

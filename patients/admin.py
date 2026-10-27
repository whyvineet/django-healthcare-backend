from django.contrib import admin

from patients.models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "date_of_birth", "phone", "created_by", "created_at")
    list_filter = ("created_by",)
    search_fields = ("name", "phone")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

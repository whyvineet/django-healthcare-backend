from django.contrib import admin

from mappings.models import PatientDoctorMapping


@admin.register(PatientDoctorMapping)
class PatientDoctorMappingAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "doctor", "assigned_by", "created_at")
    list_filter = ("assigned_by",)
    search_fields = ("patient__name", "doctor__name")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

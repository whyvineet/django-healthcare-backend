from django.contrib import admin

from doctors.models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "specialization", "email", "phone", "created_by", "created_at")
    list_filter = ("specialization",)
    search_fields = ("name", "specialization", "email")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)

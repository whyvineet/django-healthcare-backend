from rest_framework import permissions


class IsDoctorCreatorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user and (request.user.is_staff or request.user.is_superuser):
            return True
        return obj.created_by == request.user

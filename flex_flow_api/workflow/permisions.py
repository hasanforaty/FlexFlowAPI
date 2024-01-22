from rest_framework import permissions


class IsOwnerOfObject(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method not in permissions.SAFE_METHODS:
            return obj.create_by == request.user
        return True

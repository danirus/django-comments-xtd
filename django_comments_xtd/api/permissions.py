from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Only allowed when the object belongs to the request.user.
        return obj.user == request.user

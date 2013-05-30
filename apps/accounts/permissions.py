from rest_framework import permissions


class IsCurrentUser(permissions.BasePermission):
    """
    Custom permission to only allow the currently logged in user.
    """
    def has_object_permission(self, request, view, obj):
        # Write permissions are only allowed if the object is the logged in user.
        return obj == request.user

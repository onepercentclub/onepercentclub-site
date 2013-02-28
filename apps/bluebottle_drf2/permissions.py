from rest_framework import permissions


# TODO: Add write permission for 1%CREW / Assistants.
class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of an object to edit it.
    Model instances are expected to include an `author` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request, so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed if the author is the logged in user.
        return obj.author == request.user


class AllowNone(permissions.BasePermission):
    """
    Allow no access.
    """

    def has_permission(self, request, view):
        return False

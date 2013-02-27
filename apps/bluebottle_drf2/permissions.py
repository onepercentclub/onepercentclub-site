from rest_framework import permissions


# TODO: Add write permission for 1%CREW / Assistants.
class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of an object to edit it.
    Model instances are expected to include an `author` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the author of the reaction.
        return obj.author == request.user


class AllowNone(permissions.BasePermission):
    """
    Allow no access.
    """

    def has_object_permission(self, request, view, obj):
        return False

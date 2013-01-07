from rest_framework import permissions


# TODO: Add write permission for 1%CREW / Assistants.
class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow author of an object to edit it.
    """

    def has_permission(self, request, view, obj=None):
        # Skip the check unless this is an object-level test.
        if obj is None:
            return True

        # Read permissions are allowed to any request.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the author of the reaction.
        return obj.author == request.user

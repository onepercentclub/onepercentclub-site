from rest_framework import permissions

# TODO Add write permission for logged in user or 1%CREW.
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_permission(self, request, view, obj=None):
        # Skip the check unless this is an object-level test.
        if obj is None:
            return True

        # Read permissions are allowed to any request.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the reaction.
        return obj.owner == request.user

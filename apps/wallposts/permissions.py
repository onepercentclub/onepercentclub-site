from apps.wallposts.models import WallPost, MediaWallPost
from rest_framework import permissions


# TODO: Add write permission for 1%CREW / Assistants.
class IsConnectedWallPostAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only adding a photo to mediawallpost author.
    Model instances are expected to include an `mediawallpost` attribute.
    Also check if the user is the photo (or other object) author.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request, so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Look for the Wallpost that the user is trying to set.
        mediawallpost_id = request.DATA.get('mediawallpost', None)
        if mediawallpost_id:
            try:
                mediawallpost = MediaWallPost.objects.get(pk=mediawallpost_id)
            except MediaWallPost.DoesNotExist:
                return False
        else:
            # If the user isn't trying to set a wallpost, than we can carry on.
            return True

        if mediawallpost.author == request.user:
            return True

        return False
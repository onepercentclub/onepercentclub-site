from rest_framework import permissions


class IsAuthor(permissions.IsAuthenticated):
    """
    Allows write access to author.
    """
    def has_permission(self, request, view, obj=None):
        if not obj:
            obj = view.get_object()
        if request.user and request.user.is_authenticated() and obj.author == request.user:
            return True
        return False

class IsAuthorOrReadOnly(IsAuthor):
    """
    Allows write access to author otherwise read access.
    """
    def has_permission(self, request, view, obj=None):
        # If we don't have an object, we get it from the view.
        # Don't know why the view isn't passing it in the first place...
        if not obj:
            obj = view.get_object()
        if (request.method in permissions.SAFE_METHODS or 
            request.user and request.user.is_authenticated() and obj.author == request.user):
            return True
        return False

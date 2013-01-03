from rest_framework import permissions


class IsAuthor(permissions.IsAuthenticated):
    """
    Allows write access to author.
    """
    def has_permission(self, request, view, obj=None):
        if obj and request.user and request.user.is_authenticated() and obj.author == request.user:
            return True
        return False

class IsAuthorOrReadOnly(IsAuthor):
    """
    Allows write access to author otherwise read access.
    """
    def has_permission(self, request, view, obj=None):
        print obj
        print request.DATA
        print request.QUERY_PARAMS
        if (request.method in permissions.SAFE_METHODS or 
            request.user and request.user.is_authenticated() and obj.author == request.user):
            return True
        return False

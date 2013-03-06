from rest_framework import permissions
from .models import Project


class IsProjectOwnerOrReadOnly(permissions.BasePermission):
    """
    Allows access only to project owner.
    """

    def _get_project_from_request(self, request):
        if request.DATA:
            project_slug = request.DATA.get('project', None)
        else:
            project_slug = request.QUERY_PARAMS.get('project', None)
        if project_slug:
            try:
                project = Project.objects.get(slug=project_slug)
            except Project.DoesNotExist:
                return None
        else:
            return None
        return project

    def has_permission(self, request, view):
        # Read permissions are allowed to any request, so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Test for objects/lists related to a Project (e.g WallPosts).
        # Get the project form the request
        project = self._get_project_from_request(request)
        return project and project.owner == request.user

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request, so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Test for project model object-level permissions.
        return isinstance(obj, Project) and obj.owner == request.user

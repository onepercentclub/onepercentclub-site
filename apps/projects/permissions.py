from rest_framework import permissions
from .models import Project


class IsProjectOwner(permissions.BasePermission):
    """
    Allows access only to project owner.

    """
    def get_project_from_request(self, request):
        if request.DATA:
            project_id = request.DATA.get('project_id', None)
        else:
            project_id = request.QUERY_PARAMS.get('project_id', None)
        if project_id:
            project = Project.objects.get(pk=project_id)
        if not project_id or not project:
            return None
        return project
    

    def has_permission(self, request, view, obj=None):

        # Test for project model object-level
        if isinstance(obj, Project) and obj.owner == request.user:
            return True

        # Test for objects/lists related to a Project (e.g WallPosts).
        # Get the project form the request
        project = self.get_project_from_request(request)
        if project and project.owner == request.user:
            return True

        return False


class IsProjectOwnerOrReadOnly(IsProjectOwner):
    """
    Allows access only to project owner.
    """
    def has_permission(self, request, view, obj=None):

        if request.method in permissions.SAFE_METHODS:
            return True

        return super(IsProjectOwnerOrReadOnly, self).has_permission(request, view, obj)

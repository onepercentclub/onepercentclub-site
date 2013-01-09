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
            # TODO: Should throw some Exception here?
            return None
        return project
    

    def has_permission(self, request, view, obj=None):
        # If called from projects API we can expect obj to be a Project
        # or it might be available through view.get_object()
        # for now we just get it from the request.
        project = self.get_project_from_request(request)
        if project and project.owner == request.user:
            return True
        return False


class IsProjectOwnerOrReadOnly(IsProjectOwner):
    """
    Allows access only to project owner.
    """
    def has_permission(self, request, view, obj=None):
        if not obj:
            project = self.get_project_from_request(request)
        if (request.method in permissions.SAFE_METHODS or 
            project and project.owner == request.user):
            return True
        return False

from rest_framework import permissions
from .models import Project



class IsProjectOwner(permissions.IsAuthenticated):
    """
    Allows access only to project owner.
    """
    def get_project_from_request(self, request):
        # If called from another API through JSON project_id should be in request.DATA
        if request.DATA:
            project_id = request.DATA.get('project_id', None)
        else:
            # This is just here for use of the HTML API
            project_id = request.QUERY_PARAMS.get('project_id', None)
        print project_id
        if project_id:
            project = Project.objects.get(pk=project_id)
        if not project_id or not project:
            # TODO: We should throw some nice Exception here!
            return None
        return project
    

    def has_permission(self, request, view, obj=None):
        # If called from projects API we can expect obj to be a Project
        if isinstance(obj, Project):
            project = obj
        else:
            project = self.get_project_from_request(request)
        if project and request.user and request.user.is_authenticated() and project.owner == request.user:
            return True
        return False


class IsProjectOwnerOrReadOnly(IsProjectOwner):
    """
    Allows access only to project owner.
    """
    def has_permission(self, request, view, obj=None):
        if isinstance(obj, Project):
            project = obj
        else:
            project = self.get_project_from_request(request)
        if (request.method in permissions.SAFE_METHODS or 
            project and request.user and request.user.is_authenticated() 
            and project.owner == request.user):
            return True
        return False

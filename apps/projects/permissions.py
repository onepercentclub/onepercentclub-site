from bluebottle.bb_projects.models import ProjectPhase
from django.core.exceptions import ImproperlyConfigured
from rest_framework import permissions
from .models import Project


class BaseIsUser(permissions.BasePermission):
    """
    Experimental base permission to check if a user matches a certain property or field of an object or model instance.

    Usage::

        SomeApiView(...):
            permission_classes = (IsUser('project.owner'),)
    """
    field = None

    def has_object_permission(self, request, view, obj):
        if self.field is None:
            raise ImproperlyConfigured('The "IsUser" permission should provide a field attribute.')

        o = obj
        for f in self.field.split('.'):
            o = getattr(o, f, None)

        return o == request.user


IsUser = lambda x: type('IsUser', (BaseIsUser,), {'field': x})


def get_project_from_request(request):
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


class IsProjectOwner(permissions.BasePermission):
    """
    Allows access only to project owner.
    """
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Project):
            return obj.owner == request.user
        print obj.project.owner == request.user
        return obj.project.owner == request.user

    def has_permission(self, request, view):
        # Test for objects/lists related to a Project (e.g BudgetLines).
        # Get the project from the request
        project = get_project_from_request(request)
        # If we don't have a project then don't complain.
        if not project:
            return True
        return project.owner == request.user


class IsOwner(permissions.BasePermission):
    """
    Allows access only to project owner.
    """
    def has_object_permission(self, request, view, obj):
        # Test for project model object-level permissions.
        return isinstance(obj, Project) and obj.owner == request.user


class IsProjectOwnerOrReadOnly(permissions.BasePermission):
    """
    Allows access only to project owner.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request, so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Test for objects/lists related to a Project (e.g WallPosts).
        # Get the project form the request
        project = get_project_from_request(request)
        return project and project.owner == request.user

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request, so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Test for project model object-level permissions.
        return isinstance(obj, Project) and obj.owner == request.user




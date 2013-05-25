from apps.tasks.models import TaskMember
from rest_framework import permissions
from .models import Task


class IsTaskAuthorOrReadOnly(permissions.BasePermission):
    """
    Allows access only to task author.
    """

    def _get_task_from_request(self, request):
        if request.DATA:
            task_id = request.DATA.get('task', None)
        else:
            task_id = request.QUERY_PARAMS.get('task', None)
        if task_id:
            try:
                task = Task.objects.get(pk=task_id)
            except Task.DoesNotExist:
                return None
        else:
            return None
        return task

    def has_permission(self, request, view):
        # Read permissions are allowed to any request, so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Test for objects/lists related to a Task (e.g TaskMember).
        # Get the project form the request
        task = self._get_task_from_request(request)
        return task.author == request.user

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request, so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Test for project model object-level permissions.
        if isinstance(obj, Task):
            return obj.author == request.user

        if isinstance(obj, TaskMember):
            return obj.task.author == request.user


class IsMemberOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request, so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Test for project model object-level permissions.
        return isinstance(obj, TaskMember) and obj.member == request.user


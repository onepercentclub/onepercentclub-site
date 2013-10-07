from rest_framework import permissions


class IsUser(permissions.BasePermission):
    """ Read / write permissions are only allowed if the obj.user is the logged in user. """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


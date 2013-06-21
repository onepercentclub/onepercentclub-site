from apps.organizations.models import Organization
from rest_framework import permissions

class IsOrganizationMember(permissions.BasePermission):
    """
    Allows access only to organization members
    """

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Organization):
            return request.user.id in obj.organizationmember_set.values_list('user_id', flat=True)
        return request.user.id in obj.organization.organizationmember_set.values_list('user_id', flat=True)


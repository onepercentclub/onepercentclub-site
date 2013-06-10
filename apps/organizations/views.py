from apps.organizations.models import Organization, OrganizationMember
from apps.organizations.permissions import IsOrganizationMember
from apps.organizations.serializers import OrganizationSerializer, ManageOrganizationSerializer
from django.utils.translation import ugettext as _
from rest_framework import generics


class OrganizationList(generics.ListAPIView):
    model = Organization
    serializer_class = OrganizationSerializer
    paginate_by = 10


class OrganizationDetail(generics.RetrieveAPIView):
    model = Organization
    serializer_class = OrganizationSerializer


class ManageOrganizationList(generics.ListCreateAPIView):
    model = Organization
    serializer_class = ManageOrganizationSerializer
    paginate_by = 10

    # Limit the view to only the organizations the current user is member of
    def get_queryset(self):
        org_ids = OrganizationMember.objects.filter(user=self.request.user).values_list('organization_id', flat=True).all()
        queryset = super(ManageOrganizationList, self).get_queryset()
        queryset = queryset.filter(id__in=org_ids)
        return queryset


class ManageOrganizationDetail(generics.RetrieveUpdateAPIView):
    model = Organization
    serializer_class = ManageOrganizationSerializer
    permission_classes = (IsOrganizationMember, )



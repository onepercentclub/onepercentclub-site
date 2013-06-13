from apps.organizations.models import Organization, OrganizationMember, OrganizationAddress
from apps.organizations.permissions import IsOrganizationMember
from apps.organizations.serializers import OrganizationSerializer, ManageOrganizationSerializer, OrganizationAddressSerializer
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

    def post_save(self, obj, created=False):
        if created:
            member = OrganizationMember(organization=obj, member=self.request.user)
            member.save()


class ManageOrganizationDetail(generics.RetrieveUpdateAPIView):
    model = Organization
    serializer_class = ManageOrganizationSerializer
    permission_classes = (IsOrganizationMember, )


class ManageOrganizationAddressList(generics.ListCreateAPIView):
    model = OrganizationAddress
    serializer_class = OrganizationAddressSerializer
    paginate_by = 10


    def get_queryset(self):
        """
        Override get_queryset() to filter on multiple values for 'id'
        It seems that DRF2 doesn't have a implementation for filtering against an array of ids.
        https://groups.google.com/forum/?fromgroups#!topic/django-rest-framework/vbifEyharBw

        Also filter for organization members (request user should be a member)
        """
        queryset = super(ManageOrganizationAddressList, self).get_queryset()

        org_ids = OrganizationMember.objects.filter(user=self.request.user).values_list('organization_id', flat=True).all()
        queryset = queryset.filter(organization_id__in=org_ids)
        id_list = self.request.GET.getlist('ids[]', None)
        if id_list:
            queryset = queryset.filter(id__in=id_list)
        return queryset



class ManageOrganizationAddressDetail(generics.RetrieveUpdateDestroyAPIView):
    model = OrganizationAddress
    serializer_class = OrganizationAddressSerializer
    permission_classes = (IsOrganizationMember, )


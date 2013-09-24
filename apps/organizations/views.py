import os
from django.http import HttpResponseForbidden
from bluebottle.bluebottle_utils.utils import get_client_ip
from apps.organizations.models import Organization, OrganizationMember, OrganizationAddress, OrganizationDocument
from apps.organizations.permissions import IsOrganizationMember
from apps.organizations.serializers import OrganizationSerializer, ManageOrganizationSerializer, OrganizationAddressSerializer, OrganizationDocumentSerializer
from django.http.response import HttpResponseForbidden
from django.views.generic.detail import DetailView
from rest_framework import generics

from django.shortcuts import get_object_or_404
from filetransfers.api import serve_file


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
            member = OrganizationMember(organization=obj, user=self.request.user)
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


class ManageOrganizationDocumentList(generics.ListCreateAPIView):
    model = OrganizationDocument
    serializer_class = OrganizationDocumentSerializer
    paginate_by = 20
    filter = ('organization', )

    def pre_save(self, obj):
        obj.author = self.request.user
        obj.ip_address = get_client_ip(self.request)


class ManageOrganizationDocumentDetail(generics.RetrieveUpdateDestroyAPIView):
    model = OrganizationDocument
    serializer_class = OrganizationDocumentSerializer
    paginate_by = 20
    filter = ('organization', )

    def pre_save(self, obj):
        obj.author = self.request.user
        obj.ip_address = get_client_ip(self.request)



# Non API views

# Download private documents

class OrganizationDocumentDownloadView(DetailView):

    model = OrganizationDocument

    def get(self, request, pk):
        upload = get_object_or_404(OrganizationDocument, pk=pk)
        if upload.author != request.user:
            return HttpResponseForbidden()
        file_name = os.path.basename(upload.file.name)
        return serve_file(request, upload.file, save_as=file_name)
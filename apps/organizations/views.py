from django.http import HttpResponseForbidden
from django.http.response import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView


from apps.organizations.models import Organization, OrganizationMember, OrganizationDocument
from apps.organizations.permissions import IsOrganizationMember
from apps.organizations.serializers import OrganizationSerializer, ManageOrganizationSerializer, OrganizationDocumentSerializer


from filetransfers.api import serve_file
from rest_framework import generics


from bluebottle.bluebottle_utils.utils import get_client_ip


import os


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
# OrganizationDocument handled by Bluebottle view

class RegistrationDocumentDownloadView(DetailView):
    model = Organization

    def get(self, request, pk):
        obj = self.get_object()
        if request.user.is_staff:
            f = obj.registration.file
            file_name = os.path.basename(f. name)
            return serve_file(request, f, save_as=file_name)
        return HttpResponseForbidden()
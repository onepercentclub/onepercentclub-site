from django.core.exceptions import ObjectDoesNotExist
from apps.organizations.models import OrganizationDocument
import os
from apps.bluebottle_utils.serializers import ThemeSerializer
from apps.projects.models import ProjectTheme
from django.contrib.contenttypes.models import ContentType, ContentTypeManager
from django.http.response import HttpResponseForbidden, HttpResponseNotFound
from django.views.generic.base import View
from filetransfers.api import serve_file
from rest_framework import generics
from rest_framework import views, response
from taggit.models import Tag


class ThemeList(generics.ListAPIView):
    model = ProjectTheme
    serializer_class = ThemeSerializer


class TagList(views.APIView):
    """
    All tags in use on this system
    """

    def get(self, request, format=None):

        data = [tag.name for tag in Tag.objects.all()[:20]]
        return response.Response(data)


class TagSearch(views.APIView):
    """
    Search tags in use on this system
    """

    def get(self, request, format=None, search=''):

        data = [tag.name for tag in Tag.objects.filter(name__startswith=search).all()[:20]]
        return response.Response(data)


# Non API views

# Download private documents based on content_type (id) and pk
# Only 'author' of a document is allowed
# TODO: Implement a real ACL for this

class DocumentDownloadView(View):

    def get(self, request, content_type, pk):
        type = ContentType.objects.get(pk=content_type)
        type_class = type.model_class()
        try:
            file = type_class.objects.get(pk=pk)
        except type_class.DoesNotExist:
            return HttpResponseNotFound()
        if file.author != request.user:
            return HttpResponseForbidden()
        file_name = os.path.basename(file.file.name)
        return serve_file(request, file.file, save_as=file_name)
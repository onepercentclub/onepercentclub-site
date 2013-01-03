from django.contrib.contenttypes.models import ContentType
from rest_framework import generics
from rest_framework import mixins
from rest_framework import permissions
from apps.bluebottle_utils.utils import get_client_ip
from apps.projects.models import Project
from apps.projects.permissions import IsProjectOwner, IsProjectOwnerOrReadOnly
from .permissions import IsAuthor, IsAuthorOrReadOnly
from .serializers import WallPostSerializer, ProjectWallPostSerializer, ProjectMediaWallPostSerializer, ProjectTextWallPostSerializer
from .models import WallPost, MediaWallPost, TextWallPost





class WallPostList(generics.ListCreateAPIView):
    # Please extend this. We probably don't want to use this directly. 
    model = WallPost
    serializer_class = WallPostSerializer
    paginate_by = 10

    def get_content_type(self):
        # Have a separate function for this so we can easily override it for specific WallPost APIs.
        return self.request.QUERY_PARAMS.get('content_type', None)

    def get_object_id(self):
        return self.request.QUERY_PARAMS.get('object_id', None)

    def get_queryset(self):
        objects = self.model.objects
        if self.get_content_type():
            objects = objects.for_content_type(self.get_content_type())
        if self.get_object_id():
            # TODO: We should really throw a warning if content_type is not set here.
            objects = objects.filter(object_id=self.get_object_id())
        objects = objects.order_by("-created")
        return objects


class WallPostDetail(generics.RetrieveAPIView):
    model = WallPost
    serializer_class = WallPostSerializer


# Views specific to the ProjectWallPosts:

class ProjectWallPostList(WallPostList):
    serializer_class = ProjectWallPostSerializer

    def get_content_type(self):
        return ContentType.objects.get_for_model(Project).id

    def get_object_id(self):
        # We want to be specific and use project_id here.
        # Note: We're not using the filter_fields auto-filter generation because 'project_id' is not defined on the model
        # and therefore doesn't work. This could be a bug in the DRF2 auto-filter support.
        return self.request.QUERY_PARAMS.get('project_id', None)

    def pre_save(self, obj):
        obj.author = self.request.user
        obj.ip_address = get_client_ip(self.request)


class ProjectWallPostDetail(generics.RetrieveUpdateDestroyAPIView):
    model = WallPost
    serializer_class = ProjectWallPostSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_queryset(self):
        project_type = ContentType.objects.get_for_model(Project)
        return self.model.objects.filter(content_type__pk=project_type.id).order_by('object_id').distinct('object_id')


# Views specific to the ProjectMediaWallPosts:

class ProjectMediaWallPostList(generics.ListCreateAPIView):
    model = MediaWallPost
    serializer_class = ProjectMediaWallPostSerializer
    permission_classes = (IsProjectOwnerOrReadOnly,)
    paginate_by = 10

    def pre_save(self, obj):
        obj.author = self.request.user
        # TODO: Add editor to WallPost model
        # obj.editor = obj.author
        obj.ip_address = get_client_ip(self.request)


    def get_queryset(self):
        project_type = ContentType.objects.get_for_model(Project)
        return self.model.objects.filter(content_type__pk=project_type.id)

class ProjectTextWallPostList(ProjectMediaWallPostList):
    model = TextWallPost
    serializer_class = ProjectTextWallPostSerializer


class ProjectMediaWallPostDetail(generics.RetrieveUpdateDestroyAPIView):
    model = MediaWallPost
    serializer_class = ProjectMediaWallPostSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_queryset(self):
        project_type = ContentType.objects.get_for_model(Project)
        return self.model.objects.filter(content_type__pk=project_type.id).order_by('object_id').distinct('object_id')

    def pre_save(self, obj):
        # TODO: Add last editor to WallPost model
        # obj.editor = self.request.user
        obj.ip_address = get_client_ip(self.request)


class ProjectTextWallPostDetail(generics.RetrieveUpdateDestroyAPIView):
    model = TextWallPost
    serializer_class = ProjectTextWallPostSerializer

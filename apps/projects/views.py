from rest_framework import generics
from rest_framework import permissions
from django.contrib.contenttypes.models import ContentType
from apps.wallposts.models import WallPost, MediaWallPost, TextWallPost
from apps.wallposts.views import WallPostList, WallPostDetail, MediaWallPostDetail, TextWallPostDetail
from apps.bluebottle_utils.utils import get_client_ip
from .models import Project
from .serializers import ProjectSerializer, ProjectWallPostSerializer, ProjectMediaWallPostSerializer, ProjectTextWallPostSerializer


# API views

class ProjectList(generics.ListAPIView):
    model = Project
    serializer_class = ProjectSerializer
    permissions_classes = (permissions.IsAuthenticatedOrReadOnly,)
    paginate_by = 10
    filter_fields = ('phase', 'slug')


class ProjectDetail(generics.RetrieveAPIView):
    model = Project
    serializer_class = ProjectSerializer
    permissions_classes = (permissions.IsAuthenticatedOrReadOnly,)


# Project WallPost API views

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



class ProjectMediaWallPostList(ProjectWallPostList):
    model = MediaWallPost
    serializer_class = ProjectMediaWallPostSerializer


class ProjectTextWallPostList(ProjectWallPostList):
    model = TextWallPost
    serializer_class = ProjectTextWallPostSerializer


class ProjectDetailMixin():
    def get_queryset(self):
        project_type = ContentType.objects.get_for_model(Project)
        return self.model.objects.filter(content_type__pk=project_type.id).order_by('object_id').distinct('object_id')


class ProjectWallPostDetail(WallPostDetail, ProjectDetailMixin):
    model = WallPost
    serializer_class = ProjectWallPostSerializer


class ProjectMediaWallPostDetail(MediaWallPostDetail, ProjectDetailMixin):
    serializer_class = ProjectMediaWallPostSerializer


class ProjectTextWallPostDetail(TextWallPostDetail, ProjectDetailMixin):
    serializer_class = ProjectTextWallPostSerializer


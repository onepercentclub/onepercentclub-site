from django.contrib.contenttypes.models import ContentType
from rest_framework import generics
from apps.bluebottle_drf2.views import ListAPIView, ListCreateAPIView, RetrieveDeleteAPIView, RetrieveAPIView
from apps.bluebottle_utils.utils import get_client_ip
from apps.projects.models import Project
from .serializers import WallPostSerializer, ProjectWallPostSerializer, ProjectMediaWallPostSerializer, ProjectTextWallPostSerializer
from .models import WallPost, MediaWallPost, TextWallPost


class ProjectWallPostMixin(object):

    def get_queryset(self):
        queryset = super(ProjectWallPostMixin, self).get_queryset()
        project_type = ContentType.objects.get_for_model(Project)
        queryset = queryset.filter(content_type=project_type)
        project_id = self.request.QUERY_PARAMS.get('project_id', None)
        if project_id:
            queryset = queryset.filter(object_id=project_id)
        queryset = queryset.order_by("-created")
        return queryset


class WallPostList(ListCreateAPIView):
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
        queryset = super(WallPostList, self).get_queryset()
        if self.get_content_type():
            queryset = queryset.filter(content_type=self.get_content_type())
        if self.get_object_id():
            # TODO: We should really throw a warning if content_type is not set here.
            queryset = queryset.filter(object_id=self.get_object_id())
        queryset = queryset.order_by("-created")
        return queryset

    def pre_save(self, obj):
        obj.author = self.request.user
        obj.ip_address = get_client_ip(self.request)


class WallPostDetail(RetrieveDeleteAPIView):
    model = WallPost
    serializer_class = WallPostSerializer


# Views specific to the ProjectWallPosts:

class ProjectWallPostList(ProjectWallPostMixin, ListCreateAPIView):
    model = WallPost
    serializer_class = ProjectWallPostSerializer
    paginate_by = 10


class ProjectWallPostDetail(ProjectWallPostMixin, RetrieveDeleteAPIView):
    model = WallPost
    serializer_class = ProjectWallPostSerializer


class ProjectMediaWallPostList(ProjectWallPostList):
    model = MediaWallPost
    serializer_class = ProjectMediaWallPostSerializer


class ProjectMediaWallPostDetail(ProjectWallPostDetail):
    model = MediaWallPost
    serializer_class = ProjectMediaWallPostSerializer


class ProjectTextWallPostList(ProjectWallPostList):
    model = TextWallPost
    serializer_class = ProjectTextWallPostSerializer


class ProjectTextWallPostDetail(ProjectWallPostDetail):
    model = TextWallPost
    serializer_class = ProjectTextWallPostSerializer


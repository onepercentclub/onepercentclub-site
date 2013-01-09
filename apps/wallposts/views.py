from django.contrib.contenttypes.models import ContentType
from rest_framework import generics
from rest_framework import permissions
from apps.bluebottle_utils.utils import get_client_ip
from apps.projects.models import Project
from apps.projects.permissions import IsProjectOwnerOrReadOnly
from .permissions import IsAuthorOrReadOnly
from .serializers import WallPostSerializer, ProjectWallPostSerializer, ProjectMediaWallPostSerializer, ProjectTextWallPostSerializer
from .models import WallPost, MediaWallPost, TextWallPost
from apps.bluebottle_drf2.views import ListCreateAPIView, RetrieveUpdateDeleteAPIView


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

    def pre_save(self, obj):
        if not obj.author:
            obj.author = self.request.user
        else:
            # TODO: Add editor to model then enable this
            # obj.editor = self.request.user
            pass
        obj.ip_address = get_client_ip(self.request)


class ProjectWallPostList(ProjectWallPostMixin, ListCreateAPIView):
    model = WallPost
    serializer_class = ProjectWallPostSerializer
    permission_classes = (IsProjectOwnerOrReadOnly,)
    paginate_by = 10


class ProjectWallPostDetail(ProjectWallPostMixin, RetrieveUpdateDeleteAPIView):
    model = WallPost
    serializer_class = ProjectWallPostSerializer
    permission_classes = (IsAuthorOrReadOnly,)


class ProjectMediaWallPostList(ProjectWallPostMixin, ListCreateAPIView):
    model = MediaWallPost
    serializer_class = ProjectMediaWallPostSerializer
    permission_classes = (IsProjectOwnerOrReadOnly,)
    paginate_by = 10


class ProjectMediaWallPostDetail(ProjectWallPostMixin, RetrieveUpdateDeleteAPIView):
    model = MediaWallPost
    serializer_class = ProjectMediaWallPostSerializer
    permission_classes = (IsAuthorOrReadOnly,)


class ProjectTextWallPostList(ProjectWallPostMixin, ListCreateAPIView):
    model = TextWallPost
    serializer_class = ProjectTextWallPostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    paginate_by = 10


class ProjectTextWallPostDetail(ProjectWallPostMixin, RetrieveUpdateDeleteAPIView):
    model = TextWallPost
    serializer_class = ProjectTextWallPostSerializer
    permission_classes = (IsAuthorOrReadOnly,)


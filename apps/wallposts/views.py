from django.contrib.contenttypes.models import ContentType
from apps.bluebottle_drf2.views import ListCreateAPIView, RetrieveDeleteAPIView
from apps.bluebottle_utils.utils import get_client_ip
from apps.projects.models import Project
from .serializers import ProjectWallPostSerializer, ProjectMediaWallPostSerializer, ProjectTextWallPostSerializer
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
    paginate_by = 10


class ProjectWallPostDetail(ProjectWallPostMixin, RetrieveDeleteAPIView):
    model = WallPost
    serializer_class = ProjectWallPostSerializer


class ProjectMediaWallPostList(ProjectWallPostMixin, ListCreateAPIView):
    model = MediaWallPost
    serializer_class = ProjectMediaWallPostSerializer


class ProjectMediaWallPostDetail(ProjectWallPostMixin, RetrieveDeleteAPIView):
    model = MediaWallPost
    serializer_class = ProjectMediaWallPostSerializer


class ProjectTextWallPostList(ProjectWallPostMixin, ListCreateAPIView):
    model = TextWallPost
    serializer_class = ProjectTextWallPostSerializer


class ProjectTextWallPostDetail(ProjectWallPostMixin, RetrieveDeleteAPIView):
    model = TextWallPost
    serializer_class = ProjectTextWallPostSerializer


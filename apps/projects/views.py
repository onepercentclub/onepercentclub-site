from django.views.generic.detail import DetailView
from rest_framework import generics
from rest_framework import permissions
from django.contrib.contenttypes.models import ContentType
from apps.bluebottle_drf2.views import ListCreateAPIView, RetrieveUpdateDeleteAPIView, ListAPIView
from apps.bluebottle_utils.utils import get_client_ip
from apps.projects.permissions import IsProjectOwnerOrReadOnly
from apps.bluebottle_drf2.permissions import IsAuthorOrReadOnly
from apps.wallposts.models import WallPost, MediaWallPost, TextWallPost
from .models import Project
from .serializers import (ProjectSerializer, ProjectWallPostSerializer, ProjectMediaWallPostSerializer,
                          ProjectTextWallPostSerializer)


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


class ProjectWallPostMixin(object):

    def get_queryset(self):
        queryset = super(ProjectWallPostMixin, self).get_queryset()
        project_type = ContentType.objects.get_for_model(Project)
        queryset = queryset.filter(content_type=project_type)
        project_slug = self.request.QUERY_PARAMS.get('project', None)
        if project_slug:
            try:
                project = Project.objects.get(slug=project_slug)
            except Project.DoesNotExist:
                pass
            else:
                queryset = queryset.filter(object_id=project.id)
        queryset = queryset.order_by("-created")
        return queryset

    def pre_save(self, obj):
        if not obj.author:
            obj.author = self.request.user
        else:
            obj.editor = self.request.user
        obj.ip_address = get_client_ip(self.request)


class ProjectWallPostList(ProjectWallPostMixin, ListAPIView):
    model = WallPost
    serializer_class = ProjectWallPostSerializer
    paginate_by = 4


class ProjectWallPostDetail(ProjectWallPostMixin, RetrieveUpdateDeleteAPIView):
    model = WallPost
    serializer_class = ProjectWallPostSerializer
    permission_classes = (IsAuthorOrReadOnly,)


class ProjectMediaWallPostList(ProjectWallPostMixin, ListCreateAPIView):
    model = MediaWallPost
    serializer_class = ProjectMediaWallPostSerializer
    permission_classes = (IsProjectOwnerOrReadOnly,)
    paginate_by = 4


class ProjectMediaWallPostDetail(ProjectWallPostMixin, RetrieveUpdateDeleteAPIView):
    model = MediaWallPost
    serializer_class = ProjectMediaWallPostSerializer
    permission_classes = (IsAuthorOrReadOnly,)


class ProjectTextWallPostList(ProjectWallPostMixin, ListCreateAPIView):
    model = TextWallPost
    serializer_class = ProjectTextWallPostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    paginate_by = 4


class ProjectTextWallPostDetail(ProjectWallPostMixin, RetrieveUpdateDeleteAPIView):
    model = TextWallPost
    serializer_class = ProjectTextWallPostSerializer
    permission_classes = (IsAuthorOrReadOnly,)


# Django template Views

class ProjectDetailView(DetailView):
    """ This is the project view that search engines will use. """
    model = Project
    template_name = 'project_detail.html'
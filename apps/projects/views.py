from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext as _
from apps.fund.models import Donation
from apps.projects.serializers import DonationPreviewSerializer, ManageProjectSerializer
from apps.wallposts.permissions import IsConnectedWallPostAuthorOrReadOnly
from apps.wallposts.serializers import MediaWallPostPhotoSerializer
from django.http import Http404
from django.views.generic.detail import DetailView
from rest_framework import generics
from rest_framework import permissions
from django.contrib.contenttypes.models import ContentType
from apps.bluebottle_drf2.views import ListCreateAPIView, RetrieveUpdateDeleteAPIView, ListAPIView
from apps.bluebottle_utils.utils import get_client_ip, set_author_editor_ip
from apps.projects.permissions import IsProjectOwnerOrReadOnly, IsProjectOwner, IsOwner
from apps.bluebottle_drf2.permissions import IsAuthorOrReadOnly
from apps.wallposts.models import WallPost, MediaWallPost, TextWallPost, MediaWallPostPhoto
from .models import Project
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .serializers import (ProjectSerializer, ProjectWallPostSerializer, ProjectMediaWallPostSerializer,
                          ProjectTextWallPostSerializer)


# API views

class ProjectList(generics.ListAPIView):
    model = Project
    serializer_class = ProjectSerializer
    paginate_by = 10
    filter_fields = ('phase', 'slug')


class ProjectDetail(generics.RetrieveAPIView):
    model = Project
    serializer_class = ProjectSerializer


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


class ProjectMediaWallPostPhotoList(generics.ListCreateAPIView):
    model = MediaWallPostPhoto
    serializer_class = MediaWallPostPhotoSerializer
    paginate_by = 4

    def pre_save(self, obj):
        if not obj.author:
            obj.author = self.request.user
        else:
            obj.editor = self.request.user
        obj.ip_address = get_client_ip(self.request)


class ProjectMediaWallPostPhotoDetail(RetrieveUpdateDeleteAPIView):
    model = MediaWallPostPhoto
    serializer_class = MediaWallPostPhotoSerializer
    permission_classes = (IsAuthorOrReadOnly, IsConnectedWallPostAuthorOrReadOnly)


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


class ProjectDonationList(generics.ListAPIView):
    model = Donation
    serializer_class = DonationPreviewSerializer
    paginate_by = 10
    filter_fields = ('status', )

    def get_queryset(self):
        queryset = super(ProjectDonationList, self).get_queryset()
        project_slug = self.request.QUERY_PARAMS.get('project', None)
        if project_slug:
            try:
                project = Project.objects.get(slug=project_slug)
            except Project.DoesNotExist:
                raise Http404(_(u"No %(verbose_name)s found matching the query") %
                              {'verbose_name': queryset.model._meta.verbose_name})
        else:
            raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})

        queryset = queryset.filter(project=project)
        queryset = queryset.order_by("-created")
        queryset = queryset.filter(status__in=[Donation.DonationStatuses.paid, Donation.DonationStatuses.in_progress])

        return queryset



class ManageProjectList(generics.ListCreateAPIView):
    model = Project
    serializer_class = ManageProjectSerializer
    permission_classes = (IsAuthenticated, )
    paginate_by = 10

    def get_queryset(self):
        """
        Overwrite the default to only return the Projects the currently logged in user owns.
        """
        queryset = super(ManageProjectList, self).get_queryset()
        queryset = queryset.filter(owner=self.request.user)
        return queryset

    def pre_save(self, obj):
        obj.owner = self.request.user


class ManageProjectDetail(generics.RetrieveUpdateAPIView):
    model = Project
    serializer_class = ManageProjectSerializer
    permission_classes = (IsOwner, )

# Django template Views

class ProjectDetailView(DetailView):
    """ This is the project view that search engines will use. """
    model = Project
    template_name = 'project_detail.html'


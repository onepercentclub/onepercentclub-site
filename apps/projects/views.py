from apps.projects.models import ProjectPitch, ProjectPlan, ProjectAmbassador, ProjectBudgetLine, ProjectPhases, ProjectCampaign, ProjectTheme
from django.db.models.query_utils import Q
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from apps.fund.models import Donation, DonationStatuses
from apps.projects.serializers import DonationPreviewSerializer, ManageProjectSerializer, ManageProjectPitchSerializer, ManageProjectPlanSerializer, ProjectPlanSerializer, ProjectPitchSerializer, ProjectAmbassadorSerializer, ProjectBudgetLineSerializer, ProjectPreviewSerializer, ProjectCampaignSerializer, ProjectThemeSerializer
from apps.wallposts.permissions import IsConnectedWallPostAuthorOrReadOnly
from apps.wallposts.serializers import MediaWallPostPhotoSerializer
from django.http import Http404
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
import django_filters
from rest_framework import generics
from rest_framework import permissions
from django.contrib.contenttypes.models import ContentType
from bluebottle.bluebottle_drf2.views import ListCreateAPIView, RetrieveUpdateDeleteAPIView, ListAPIView
from bluebottle.bluebottle_utils.utils import get_client_ip, set_author_editor_ip
from apps.projects.permissions import IsProjectOwnerOrReadOnly, IsProjectOwner, IsOwner, NoRunningProjectsOrReadOnly, EditablePitchOrReadOnly, EditablePlanOrReadOnly
from bluebottle.bluebottle_drf2.permissions import IsAuthorOrReadOnly
from apps.wallposts.models import WallPost, MediaWallPost, TextWallPost, MediaWallPostPhoto
from .models import Project
from rest_framework.permissions import IsAuthenticated
from .serializers import (ProjectSerializer, ProjectWallPostSerializer, ProjectMediaWallPostSerializer,
                          ProjectTextWallPostSerializer)


# API views

class ProjectPreviewList(generics.ListAPIView):
    model = Project
    serializer_class = ProjectPreviewSerializer
    paginate_by = 8
    paginate_by_param = 'page_size'
    max_paginate_by = 100

    filter_fields = ('phase', )

    def get_queryset(self):
        qs = Project.objects

        # For some reason the query fails if the country filter is defined before this.
        ordering = self.request.QUERY_PARAMS.get('ordering', None)

        if ordering == 'newest':
            qs = qs.order_by('-created')
        elif ordering == 'title':
            qs = qs.order_by('title')
        elif ordering == 'deadline':
            qs = qs.order_by('projectcampaign__deadline')
        elif ordering == 'needed':
            qs = qs.order_by('money_needed')
        elif ordering == 'popularity':
            qs = qs.order_by('-popularity')


        country = self.request.QUERY_PARAMS.get('country', None)
        if country:
            qs = qs.filter(projectplan__country=country)

        theme = self.request.QUERY_PARAMS.get('theme', None)
        if theme:
            qs = qs.filter(projectplan__theme_id=theme)

        text = self.request.QUERY_PARAMS.get('text', None)
        if text:
            qs = qs.filter(Q(title__icontains=text) |
                           Q(projectplan__pitch__icontains=text) |
                           Q(projectplan__description__icontains=text) |
                           Q(projectplan__title__icontains=text))

        qs = qs.exclude(phase=ProjectPhases.pitch)
        qs = qs.exclude(phase=ProjectPhases.failed)

        return qs


class ProjectPreviewDetail(generics.RetrieveAPIView):
    model = Project
    serializer_class = ProjectPreviewSerializer

    def get_queryset(self):
        qs = super(ProjectPreviewDetail, self).get_queryset()
        qs = qs.exclude(phase=ProjectPhases.pitch)
        return qs


class ProjectList(generics.ListAPIView):
    model = Project
    serializer_class = ProjectSerializer
    paginate_by = 10
    filter_fields = ('phase', )

    def get_queryset(self):
        qs = super(ProjectList, self).get_queryset()
        qs = qs.exclude(phase=ProjectPhases.pitch)
        return qs


class ProjectDetail(generics.RetrieveAPIView):
    model = Project
    serializer_class = ProjectSerializer

    def get_queryset(self):
        qs = super(ProjectDetail, self).get_queryset()
        qs = qs.exclude(phase=ProjectPhases.pitch)
        return qs


class ProjectPitchDetail(generics.RetrieveAPIView):
    model = ProjectPitch
    serializer_class = ProjectPitchSerializer


class ProjectPlanDetail(generics.RetrieveAPIView):
    model = ProjectPlan
    serializer_class = ProjectPlanSerializer


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
    paginate_by = 40


class ProjectWallPostDetail(ProjectWallPostMixin, RetrieveUpdateDeleteAPIView):
    model = WallPost
    serializer_class = ProjectWallPostSerializer
    permission_classes = (IsAuthorOrReadOnly,)


class ProjectMediaWallPostPhotoList(ListCreateAPIView):
    model = MediaWallPostPhoto
    serializer_class = MediaWallPostPhotoSerializer
    paginate_by = 4

    def pre_save(self, obj):
        if not obj.author:
            obj.author = self.request.user
        else:
            obj.editor = self.request.user
        obj.ip_address = get_client_ip(self.request)

    def create(self, request, *args, **kwargs): #FIXME
        """
        Work around browser issues.

        Adding photos to a wallpost works correctly in Chrome. Firefox (at least
        FF 24) sends the ```mediawallpost``` value to Django with the value 
        'null', which is then interpreted as a string in Django. This is 
        incorrect behaviour, as ```mediawallpost``` is a relation.

        Eventually, this leads to HTTP400 errors, effectively breaking photo
        uploads in FF.

        The quick fix is detecting this incorrect 'null' string in ```request.POST```
        and setting it to an empty string. ```request.POST``` is mutable because
        of the multipart nature.

        NOTE: This is something that should be fixed in the Ember app or maybe even
        Ember itself.
        """
        post = request.POST.get('mediawallpost', False)
        if post and post == u'null':
            request.POST['mediawallpost'] = u''
        return super(ProjectMediaWallPostPhotoList, self).create(request, *args, **kwargs)


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
        queryset = queryset.order_by("-ready")
        queryset = queryset.filter(status__in=[DonationStatuses.paid, DonationStatuses.pending])

        return queryset


class ManageProjectList(generics.ListCreateAPIView):
    model = Project
    serializer_class = ManageProjectSerializer
    permission_classes = (IsAuthenticated, NoRunningProjectsOrReadOnly, )
    paginate_by = 10

    def get_queryset(self):
        """
        Overwrite the default to only return the Projects the currently logged in user owns.
        """
        queryset = super(ManageProjectList, self).get_queryset()
        queryset = queryset.filter(owner=self.request.user)
        queryset = queryset.order_by('-created')
        return queryset

    def pre_save(self, obj):
        obj.owner = self.request.user


class ManageProjectDetail(generics.RetrieveUpdateAPIView):
    model = Project
    serializer_class = ManageProjectSerializer
    permission_classes = (IsProjectOwner, )


class ManageProjectPitchDetail(generics.RetrieveUpdateAPIView):
    model = ProjectPitch
    serializer_class = ManageProjectPitchSerializer
    permission_classes = (EditablePitchOrReadOnly, IsProjectOwner, )


class ManageProjectPlanDetail(generics.RetrieveUpdateAPIView):
    model = ProjectPlan
    serializer_class = ManageProjectPlanSerializer
    permission_classes = (EditablePlanOrReadOnly, IsProjectOwner, )


class ManageProjectAmbassadorList(generics.ListCreateAPIView):
    model = ProjectAmbassador
    serializer_class = ProjectAmbassadorSerializer
    paginate_by = 20


class ManageProjectAmbassadorDetail(generics.RetrieveUpdateDestroyAPIView):
    model = ProjectAmbassador
    serializer_class = ProjectAmbassadorSerializer


class ManageProjectBudgetLinetList(generics.ListCreateAPIView):
    model = ProjectBudgetLine
    serializer_class = ProjectBudgetLineSerializer
    paginate_by = 20


class ManageProjectBudgetLineDetail(generics.RetrieveUpdateDestroyAPIView):
    model = ProjectBudgetLine
    serializer_class = ProjectBudgetLineSerializer


class ManageProjectCampaignDetail(generics.RetrieveUpdateAPIView):
    model = ProjectCampaign
    serializer_class = ProjectCampaignSerializer
    permission_classes = (EditablePlanOrReadOnly, IsProjectOwner, )


# Django template Views

class ProjectDetailView(DetailView):
    """ This is the project view that search engines will use. """
    model = Project
    template_name = 'project_detail.html'


class ProjectIframeView(DetailView):
    model = Project
    template_name = 'project_iframe.html'

    @method_decorator(xframe_options_exempt)
    def dispatch(self, *args, **kwargs):
        return super(ProjectIframeView, self).dispatch(*args, **kwargs)

# class MacroMicroListView(ListView):
#     model = Project
#     queryset = Project.objects.filter(partner_organization__slug='macro_micro')
#
#
#     def render_to_response(self, context, **response_kwargs):
#         return super(MacroMicroListView, self).render_to_response(
#             context,
#             mimetype='application/xml',
#             **response_kwargs)


class ProjectThemeList(generics.ListAPIView):
    model = ProjectTheme
    serializer_class = ProjectThemeSerializer



class ProjectThemeDetail(generics.RetrieveAPIView):
    model = ProjectTheme
    serializer_class = ProjectThemeSerializer


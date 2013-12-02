import django_filters

from django.db.models.query_utils import Q
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.http import Http404
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic.detail import DetailView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.projects.models import ProjectPitch, ProjectPlan, ProjectAmbassador, ProjectBudgetLine, ProjectPhases, ProjectCampaign, ProjectTheme
from apps.fund.models import Donation, DonationStatuses
from apps.projects.serializers import ProjectSupporterSerializer, ManageProjectSerializer, ManageProjectPitchSerializer, ManageProjectPlanSerializer, ProjectPlanSerializer, ProjectPitchSerializer, ProjectAmbassadorSerializer, ProjectBudgetLineSerializer, ProjectPreviewSerializer, ProjectCampaignSerializer, ProjectThemeSerializer
from apps.projects.permissions import IsProjectOwner, NoRunningProjectsOrReadOnly, EditablePitchOrReadOnly, EditablePlanOrReadOnly
from apps.fundraisers.models import FundRaiser

from .models import Project
from .serializers import ProjectSerializer, ProjectDonationSerializer

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
        elif ordering == 'money_needed':
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


class ProjectSupporterList(generics.ListAPIView):
    model = Donation
    serializer_class = ProjectSupporterSerializer
    paginate_by = 10
    filter_fields = ('status', )

    def get_queryset(self):
        queryset = super(ProjectSupporterList, self).get_queryset()

        filter_kwargs = {}

        project_slug = self.request.QUERY_PARAMS.get('project', None)
        if project_slug:
            try:
                project = Project.objects.get(slug=project_slug)
                filter_kwargs['project'] = project
            except Project.DoesNotExist:
                raise Http404(_(u"No %(verbose_name)s found matching the query") %
                              {'verbose_name': queryset.model._meta.verbose_name})
        else:
            raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': Project._meta.verbose_name})

        fundraiser_id = self.request.QUERY_PARAMS.get('fundraiser', None)
        if fundraiser_id:
            try:
                fundraiser = FundRaiser.objects.get(project=project, pk=fundraiser_id)
                filter_kwargs['fundraiser'] = fundraiser
            except FundRaiser.DoesNotExist:
                raise Http404(_(u"No %(verbose_name)s found matching the query") %
                              {'verbose_name': FundRaiser._meta.verbose_name})

        queryset = queryset.filter(**filter_kwargs)
        queryset = queryset.order_by("-ready")
        queryset = queryset.filter(status__in=[DonationStatuses.paid, DonationStatuses.pending])

        return queryset


class ProjectDonationList(ProjectSupporterList):
    """
    Returns a list of donations made to this project or fundraiser action.
    """
    serializer_class = ProjectDonationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):

        # The super handles basic filtering.
        queryset = super(ProjectDonationList, self).get_queryset()

        project_slug = self.request.QUERY_PARAMS.get('project', None)
        fundraiser_id = self.request.QUERY_PARAMS.get('fundraiser', None)

        filter_kwargs = {}

        if fundraiser_id:
            filter_kwargs['fundraiser__owner'] = self.request.user
        elif project_slug:
            filter_kwargs['project__owner'] = self.request.user
        else:
            return queryset.none()

        return queryset.filter(**filter_kwargs)


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


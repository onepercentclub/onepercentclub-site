from apps.projects.models import ProjectBudgetLine
from bluebottle.bb_projects.views import ProjectPreviewList
from bluebottle.geo.models import Country
from bluebottle.geo.serializers import CountrySerializer
import django_filters

from django.db.models.query_utils import Q
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.http import Http404
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic.detail import DetailView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.fund.models import Donation, DonationStatuses
from apps.projects.serializers import (
    ProjectSupporterSerializer, ProjectPreviewSerializer, ProjectThemeSerializer, ProjectBudgetLineSerializer)
from apps.projects.permissions import IsProjectOwner
from apps.fundraisers.models import FundRaiser
from bluebottle.utils.utils import get_project_model

from .models import Project
from .serializers import ProjectSerializer, ProjectDonationSerializer


class ManageProjectBudgetLineList(generics.ListCreateAPIView):
    model = ProjectBudgetLine
    serializer_class = ProjectBudgetLineSerializer
    paginate_by = 50
    permission_classes = (IsProjectOwner, )


class ManageProjectBudgetLineDetail(generics.RetrieveUpdateDestroyAPIView):
    model = ProjectBudgetLine
    serializer_class = ProjectBudgetLineSerializer
    permission_classes = (IsProjectOwner, )


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


class MacroMicroListView(generics.ListAPIView):
    model = Project
    queryset = Project.objects.filter(partner_organization__slug='macro_micro')


    def render_to_response(self, context, **response_kwargs):
        return super(MacroMicroListView, self).render_to_response(
            context,
            mimetype='application/xml',
            **response_kwargs)

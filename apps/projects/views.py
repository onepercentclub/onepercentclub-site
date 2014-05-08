from apps.projects.models import ProjectBudgetLine

from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic.detail import DetailView
from rest_framework import generics

from apps.projects.serializers import  ProjectBudgetLineSerializer
from apps.projects.permissions import IsProjectOwner

from .models import Project


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



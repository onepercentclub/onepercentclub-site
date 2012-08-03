from django.views.generic import ListView, DetailView

from .models import Project


class ProjectViewBase(object):
    model = Project


class ProjectListView(ProjectViewBase, ListView):
    template_name = 'projects/list.html'


class ProjectDetailView(ProjectViewBase, DetailView):
    template_name = 'projects/detail.html'


class ProjectMapView(ProjectViewBase, DetailView):
    template_name = "projects/map.html"


class ProjectSearchView(ProjectViewBase, ListView):
    template_name = "projects/search.html"


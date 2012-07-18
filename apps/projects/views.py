#from django.shortcuts import render_to_response, get_object_or_404, RequestContext
#from .models import Project

#def ProjectDetailView(request, slug):
#    project = get_object_or_404(Project, slug=slug)
#    variables = RequestContext(request, {})
#    return render_to_response('projects/view.html', {'project': project}, variables)

from django.views.generic import ListView, DetailView

from .models import Project


class ProjectViewBase(object):
    model = Project


class ProjectListView(ProjectViewBase, ListView):
    pass


class ProjectDetailView(ProjectViewBase, DetailView):
    pass

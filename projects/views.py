import logging
logger = logging.getLogger(__name__)
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from projects.models import Project

def overview(request):
    variables = RequestContext(request, {})
    projects = Project.objects.all().filter(status = 'validated').order_by('title')
    return render_to_response('projects/overview.html', {'projects': projects}, variables)

def view(request, name):
    variables = RequestContext(request, {})
    project = Project.objects.get(name = name)
    return render_to_response('projects/view.html', {'project': project}, variables)



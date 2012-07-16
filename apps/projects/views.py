from django.shortcuts import render_to_response, get_object_or_404, RequestContext
from .models import Project

def view(request, slug):
    project = get_object_or_404(Project, slug=slug)
    variables = RequestContext(request, {})
    return render_to_response('projects/view.html', {'project': project}, variables)

from django.http import HttpResponse
from django.views.generic import View
from apps.projects.models import Project
from django.template.loader import render_to_string
import json

class WidgetView(View):
    template = "widget/widget.html"

    def get(self, request, *args, **kwargs):

        callback = request.GET.get('callback', None)

        id = request.GET.get('id', None)
        height = request.GET.get('height', None)
        width  = request.GET.get('width', None)
        partner = request.GET.get('partner', None)
        
        projects = None

        if id and not partner:
            try:
                projects = Project.filter(id=id) #Enforce that we always get a QuerySet for use in the template
            except Project.DoesNotExist:
                pass
        elif partner:
            projects = Project.objects.filter(partner_organization__slug=partner).order_by('?')[:3]
        else:
            projects = Project.objects.all().order_by('?')[:3]            

        html = render_to_string(self.template, locals())
        response_data = "%s ( {'html': %s } )" % (callback, json.dumps(html))
        return HttpResponse(response_data, content_type="text/javascript") 
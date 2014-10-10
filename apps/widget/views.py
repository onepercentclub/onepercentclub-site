from django.http import HttpResponse
from django.views.generic import View
from apps.projects.models import Project
from django.template.loader import render_to_string
import json

class WidgetView(View):
    template = "widget/widget.html"

    def get(self, request, *args, **kwargs):

        print request.GET
        callback = request.GET.get('callback', None)
        id = request.GET.get('id', None)
        height = request.GET.get('height', None)
        width  = request.GET.get('width', None)
        partner = request.GET.get('partner', None)

        if id:
            try:
                projects = Project.objects.filter(id=id)
            except Project.DoesNotExist:
                project = None
        else:
            projects = Project.objects.all()[0:10]



        html = render_to_string(self.template, locals())
        print "HTML: ", html
        print "Callback", callback
        
        #if callback:
        #  response_data = "{0} ({'html': '{1}'' })".format(callback, json.dumps(html))
        response_data = "%s ( {'html': %s } )" % (callback, json.dumps(html))
        print "Response: ", response_data
        return HttpResponse(response_data, content_type="text/javascript") 
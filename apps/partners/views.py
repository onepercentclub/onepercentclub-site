from apps.partners.serializers import PartnerOrganizationSerializer
from apps.projects.models import Project, PartnerOrganization
from django.contrib.sites.models import Site
from django.views.generic.list import ListView
from rest_framework import generics


# API view

class PartnerDetail(generics.RetrieveAPIView):
    model = PartnerOrganization
    serializer_class = PartnerOrganizationSerializer


# Django view

class MacroMicroListView(ListView):

    template_name = 'macromicro_list.html'
    model = Project
    queryset = Project.objects.filter(partner_organization__slug='macro_micro')

    def render_to_response(self, context, **response_kwargs):
        return super(MacroMicroListView, self).render_to_response(
            context,
            mimetype='application/xml',
            **response_kwargs)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(MacroMicroListView, self).get_context_data(**kwargs)
        if Site.objects.get_current().domain in ['localhost:8000', '127.0.0.1:8000']:
            site = 'http://' + Site.objects.get_current().domain
        else:
            site = 'https://' + Site.objects.get_current().domain
        context['site'] = site
        return context


from apps.projects.models import Project
from django.views.generic.list import ListView


class MacroMicroListView(ListView):

    template_name = 'macromicro_list.html'
    model = Project
    queryset = Project.objects.filter(partner_organization__slug='macro_micro')

    def render_to_response(self, context, **response_kwargs):
        return super(MacroMicroListView, self).render_to_response(
            context,
            mimetype='application/xml',
            **response_kwargs)
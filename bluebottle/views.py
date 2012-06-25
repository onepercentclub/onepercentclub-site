import logging
logger = logging.getLogger(__name__)

from django.template import RequestContext, Context, loader
from django.http import HttpResponseServerError

from django.views.generic import TemplateView


def handler500(request, template_name='500.html'):
    """
    500 error handler which tries to use a RequestContext - unless an error
    is raised, in which a normal Context is used with just the request
    available.

    Templates: `500.html`
    Context: None
    """

    # Try returning using a RequestContext
    try:
        context = RequestContext(request)
    except:
        logger.warn('Error getting RequestContext for ServerError page.')
        context = Context({'request': request})

    t = loader.get_template('500.html') # You need to create a 500.html template.
    return HttpResponseServerError(t.render(context))


class HomeView(TemplateView):
    """
    Home view for the site.
    """

    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        """ Add some extra context. """
        context = {}

        return context

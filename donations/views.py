import logging
logger = logging.getLogger(__name__)
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from donations.models import Thanks

def thanks(request):
    variables = RequestContext(request, {})
    thanks = Thanks.objects.all().order_by('create_date')
    return render_to_response('donations/thanks.html', {'thanks': thanks}, variables)



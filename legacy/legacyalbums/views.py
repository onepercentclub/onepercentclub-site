import logging
logger = logging.getLogger(__name__)
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from donations.models import Thanks

def overview(request, catalog_id):
    variables = RequestContext(request, {})
    albums = Thanks.objects.filter(catalog_id = catalog_id).all().order_by('create_date')
    return render_to_response('legacyalbums/overview.html', {'legacyalbums': albums}, variables)



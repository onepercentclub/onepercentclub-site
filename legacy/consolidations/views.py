from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from consolidations.models import Consolidation,Settlement

def overview(request):
    variables = RequestContext(request, {})
    consolidations = Consolidation.objects.all().order_by('-created')[0:20]
    return render_to_response('consolidations/overview.html', {'consolidations': consolidations}, variables)

def settlement(request, id):
    variables = RequestContext(request, {})
    settlement = Settlement.objects.get(pk = id)
    return render_to_response('consolidations/settlement.html', {'settlement': settlement}, variables)



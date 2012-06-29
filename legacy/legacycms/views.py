from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from news.models import Item

def overview(request):
    variables = RequestContext(request, {})
    pages = Page.objects.all().order_by('slug')
    return render_to_response('legacycms/overview.html', {'pages': pages}, variables)

def view(request, slug):
    variables = RequestContext(request, {})
    page = Page.objects.get(slug = slug)
    return render_to_response('legacycms/view.html', {'page': page}, variables)



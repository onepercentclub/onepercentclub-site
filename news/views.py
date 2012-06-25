from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from news.models import Item

def overview(request):
    variables = RequestContext(request, {})
    items = Item.objects.all().order_by('-created')[0:20]
    return render_to_response('news/overview.html', {'items': items}, variables)

def view(request, id):
    variables = RequestContext(request, {})
    item = Item.objects.get(pk = id)
    return render_to_response('news/view.html', {'item': item}, variables)



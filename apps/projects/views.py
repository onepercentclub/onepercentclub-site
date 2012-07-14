from django.shortcuts import render_to_response, get_object_or_404

def test(request):
    return render_to_response('projects/test.html')
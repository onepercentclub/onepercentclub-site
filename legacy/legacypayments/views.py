from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from payments.models import Payment,PaymentCluster

def overview(request):
    variables = RequestContext(request, {})
    paymentclusters = PaymentCluster.objects.all().order_by('-created')[0:30]
    return render_to_response('legacypayments/overview.html', {'paymentclusters': paymentclusters}, variables)

def view(request, id):
    variables = RequestContext(request, {})
    payment = Payment.objects.get(pk = id)
    return render_to_response('legacypayments/view.html', {'payment': payment}, variables)



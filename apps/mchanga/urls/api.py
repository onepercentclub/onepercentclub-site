from django.conf.urls import patterns, url
from ..views import MpesaPaymentList

urlpatterns = patterns('',
     url(r'^payments/$', MpesaPaymentList.as_view(), name='mchanga-payment-list'),
)
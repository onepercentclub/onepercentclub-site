from django.conf.urls import patterns, url
from ..views import MpesaPaymentList, MpesaFundRaiserList, MpesaFundRaiserDetail

urlpatterns = patterns('',
      url(r'^payments/$', MpesaPaymentList.as_view(), name='mchanga-payment-list'),
      url(r'^fundraisers/$', MpesaFundRaiserList.as_view(), name='mchanga-fundraiser-list'),
      url(r'^fundraisers/(?P<account>[\w-]+)$', MpesaFundRaiserDetail.as_view(), name='mchanga-fundraiser-detail'),
)

from django.conf.urls import patterns, url
from ..views import MpesaPaymentList, MpesaFundraiserList, MpesaFundraiserDetail

urlpatterns = patterns('',
      url(r'^payments/$', MpesaPaymentList.as_view(), name='mchanga-payment-list'),
      url(r'^fundraisers/$', MpesaFundraiserList.as_view(), name='mchanga-fundraiser-list'),
      url(r'^fundraisers/(?P<account>[\w-]+)$', MpesaFundraiserDetail.as_view(), name='mchanga-fundraiser-detail'),
)

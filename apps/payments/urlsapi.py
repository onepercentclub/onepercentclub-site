from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import PaymentMethodList, CurrentPaymentDetail

urlpatterns = patterns('',
    url(r'^methods/$', PaymentMethodList.as_view(), name='payments-method-list'),
    url(r'^current$', CurrentPaymentDetail.as_view(), name='payments-current-detail')
)

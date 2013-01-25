from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import PaymentMethodList, CheckoutDetail

urlpatterns = patterns('',
    url(r'^methods/$', PaymentMethodList.as_view(), name='payments-method-list'),
    url(r'^checkout', CheckoutDetail.as_view(), name='payments-current-detail')
)

from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import PaymentMethodList

urlpatterns = patterns('',
    url(r'^methods/$', PaymentMethodList.as_view(), name='payments-method-list'),

)

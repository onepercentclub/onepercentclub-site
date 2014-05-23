from django.conf.urls import patterns
from surlex.dj import surl
from ..views import PaymentDetail


urlpatterns = patterns('',
    surl(r'^payments/<pk:#>$', PaymentDetail.as_view(), name='payment-detail'),
)

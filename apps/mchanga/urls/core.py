from django.conf.urls import patterns, url
from ..views import PaymentStatusChangedView

urlpatterns = patterns(
    '',
    url(r'^status_update/(?P<payment_id>[\w]+)$', PaymentStatusChangedView.as_view(),
        name='mchanga-payment-detail-status-update'),
    url(r'^status_update/$', PaymentStatusChangedView.as_view(),
        name='mchanga-payment-status-update'),
)
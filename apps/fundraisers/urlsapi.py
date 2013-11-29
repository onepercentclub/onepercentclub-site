from surlex.dj import surl
from django.conf.urls import patterns, url

from .views import FundRaiserListView, FundRaiserDetailView


urlpatterns = patterns('',
    # TODO: filtering via querystring?
    url(r'^$', FundRaiserListView.as_view(), name='fundraiser-list'),
    surl(r'^<pk:#>$', FundRaiserDetailView.as_view(), name='fundraiser-detail'),
)

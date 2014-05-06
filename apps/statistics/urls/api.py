from django.conf.urls import patterns, url
from surlex.dj import surl
from ..views import StatisticDetail

urlpatterns = patterns('',
    url(r'^/current$', StatisticDetail.as_view(), name='stats'),
)

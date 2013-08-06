from apps.homepage.views import HomePageDetail
from django.conf.urls import patterns, url
from surlex.dj import surl


urlpatterns = patterns('',
    surl(r'^<language:s>$', HomePageDetail.as_view(), name='stats'),
)

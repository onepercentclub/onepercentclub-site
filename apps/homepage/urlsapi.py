from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import HomePageDetail


urlpatterns = patterns('',
    surl(r'^<language:s>$', HomePageDetail.as_view(), name='stats'),
)

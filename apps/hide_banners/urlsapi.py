from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import SlideList

urlpatterns = patterns('',
    url(r'^$', SlideList.as_view(), name='slide-list'),
)

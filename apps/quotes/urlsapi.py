from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import QuoteList

urlpatterns = patterns('',
    url(r'^$', QuoteList.as_view(), name='quote-list'),
)

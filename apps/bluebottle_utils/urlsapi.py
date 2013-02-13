from django.conf.urls import patterns, url
from .views import CountryList


urlpatterns = patterns('',
    url(r'^countries/$', CountryList.as_view(), name='utils-country-list')
    )
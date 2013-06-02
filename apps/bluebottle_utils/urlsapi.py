from django.conf.urls import patterns, url
from .views import ThemeList, TagList


urlpatterns = patterns('',
    url(r'^themes/$', ThemeList.as_view(), name='utils-theme-list'),
    url(r'^tags/$', TagList.as_view(), name='utils-tag-list')
    )

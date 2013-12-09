from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import GroupPageList, GroupPageDetail


urlpatterns = patterns('',
    url(r'^$', GroupPageList.as_view(), name='group-page-list'),
    surl(r'^<pk:#>$', GroupPageDetail.as_view(), name='group-page-detail'),
)

from django.conf.urls import patterns, url
from .views import MemberList, MemberDetail

urlpatterns = patterns('',
    url(r'^$', MemberList.as_view(), name='member-list'),
    url(r'^(?P<pk>[0-9]+)$', MemberDetail.as_view(), name='member-detail'),
)

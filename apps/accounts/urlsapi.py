from django.conf.urls import patterns, url
from .views import MemberList, MemberDetail, AuthenticatedMember

urlpatterns = patterns('',
    url(r'^users/$', MemberList.as_view(), name='member-list'),
    url(r'^users/(?P<pk>[0-9]+)$', MemberDetail.as_view(), name='member-detail'),
    url(r'^current$', AuthenticatedMember.as_view(), name='member-current'),
)

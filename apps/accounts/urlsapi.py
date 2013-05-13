from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import MemberList, MemberProfileDetail, AuthenticatedUser, MemberSettingsDetail

urlpatterns = patterns('',
    surl(r'^<pk:#>$', MemberProfileDetail.as_view(), name='member-profile-detail'),
    url(r'^current$', AuthenticatedUser.as_view(), name='member-current'),
    surl(r'^settings/<username:s>$', MemberSettingsDetail.as_view(), name='member-settings-detail'),
)

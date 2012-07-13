from django.conf.urls import patterns

from surlex.dj import surl

from .views import UserProfileList, UserProfileDetail


urlpatterns = patterns('',
    surl(r'^$', UserProfileList.as_view(), name='userprofile_list'),
    surl(r'^<slug:s>/$', UserProfileDetail.as_view(), name='userprofile_detail'),
)

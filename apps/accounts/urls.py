from django.conf.urls import patterns, url

from .views import UserProfileList, UserProfileDetail

# TODO Add 'members' as a setting option.
urlpatterns = patterns('',
    url(r'^members/$', UserProfileList.as_view(), name='profile'),
    url(r'^members/(?P<userslug>[0-9a-z\-]{1,30})$',
        UserProfileDetail.as_view(), name='user'),
)

from django.conf.urls import patterns

from surlex.dj import surl

from .views import UserList, UserDetail


urlpatterns = patterns('',
    surl(r'^$', UserList.as_view(), name='user_list'),
    surl(r'^<slug:s>/$', UserDetail.as_view(), name='user_detail'),
)

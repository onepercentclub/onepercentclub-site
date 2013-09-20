from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import LikeList


urlpatterns = patterns('',
    url(r'^$', LikeList.as_view(), name='like-list')
)
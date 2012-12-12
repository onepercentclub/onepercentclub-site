from django.conf.urls import patterns, url
from .views import WallPostList, WallPostDetail

urlpatterns = patterns('',
    url(r'^$', WallPostList.as_view(), name='wallpost-list'),
    url(r'^(?P<pk>[0-9]+)$', WallPostDetail.as_view(), name='wallpost-detail'),
)

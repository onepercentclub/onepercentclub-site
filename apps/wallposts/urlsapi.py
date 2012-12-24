from django.conf.urls import patterns, url
from .views import WallPostList, WallPostDetail, ProjectWallPostList, ProjectWallPostDetail

urlpatterns = patterns('',
    url(r'^$', WallPostList.as_view(), name='wallpost-list'),
    url(r'^(?P<pk>[0-9]+)$', WallPostDetail.as_view(), name='wallpost-detail'),
    url(r'^projectwallposts/$', ProjectWallPostList.as_view(), name='project-wallpost-list'),
    url(r'^projectwallposts/(?P<pk>[0-9]+)$', ProjectWallPostDetail.as_view(), name='project-wallpost-detail'),
)

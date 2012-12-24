from django.conf.urls import patterns, url
from .views import ProjectWallPostList, ProjectWallPostDetail

urlpatterns = patterns('',
    url(r'^projectwallposts/$', ProjectWallPostList.as_view(), name='project-wallpost-list'),
    url(r'^projectwallposts/(?P<pk>[0-9]+)$', ProjectWallPostDetail.as_view(), name='project-wallpost-detail'),
)

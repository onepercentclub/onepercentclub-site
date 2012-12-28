from apps.wallposts.views import ProjectMediaWallPostList, ProjectMediaWallPostDetail
from django.conf.urls import patterns, url
from .views import ProjectWallPostList, ProjectWallPostDetail

urlpatterns = patterns('',
    url(r'^projectwallposts/$', ProjectWallPostList.as_view(), name='project-wallpost-list'),
    url(r'^projectwallposts/(?P<pk>[0-9]+)$', ProjectWallPostDetail.as_view(), name='project-wallpost-detail'),
    # Temporary API for ProjectMediaWallPosts so that we test CRUD before making a generic polymorphic serializer.
    url(r'^projectmediawallposts/$', ProjectMediaWallPostList.as_view(), name='project-mediawallpost-list'),
    url(r'^projectmediawallposts/(?P<pk>[0-9]+)$', ProjectMediaWallPostDetail.as_view(), name='project-mediawallpost-detail'),
)

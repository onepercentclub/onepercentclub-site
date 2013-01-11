from apps.wallposts.views import  Project
from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import (ProjectWallPostList, ProjectWallPostDetail, ProjectMediaWallPostList,
                    ProjectMediaWallPostDetail, ProjectTextWallPostList, ProjectTextWallPostDetail)


urlpatterns = patterns('',
    # TODO: Move this to projects.
    url(r'^projectwallposts/$', ProjectWallPostList.as_view(), name='project-wallpost-list'),
    url(r'^projectwallposts/(?P<pk>[0-9]+)$', ProjectWallPostDetail.as_view(), name='project-wallpost-detail'),
    url(r'^projectmediawallposts/$', ProjectMediaWallPostList.as_view(), name='project-mediawallpost-list'),
    surl(r'^projectmediawallposts/<pk:#>$', ProjectMediaWallPostDetail.as_view(), name='project-mediawallpost-detail'),
    url(r'^projecttextwallposts/$', ProjectTextWallPostList.as_view(), name='project-textwallpost-list'),
    surl(r'^projecttextwallposts/<pk:#>$', ProjectTextWallPostDetail.as_view(), name='project-textwallpost-detail'),
)

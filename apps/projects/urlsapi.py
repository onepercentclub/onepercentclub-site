from django.conf.urls import patterns, url, include
from surlex.dj import surl
from .views import (ProjectDetail, ProjectList, ProjectWallPostList, ProjectWallPostDetail, ProjectMediaWallPostList,
                    ProjectMediaWallPostDetail, ProjectTextWallPostList, ProjectTextWallPostDetail)

urlpatterns = patterns('',
    url(r'^$', ProjectList.as_view(), name='project-list'),
    surl(r'^<pk:#>$', ProjectDetail.as_view(), name='project-detail'),

    # Project WallPost Urls
    url(r'^wallposts/$', ProjectWallPostList.as_view(), name='project-wallpost-list'),
    surl(r'^wallposts/<pk:#>$', ProjectWallPostDetail.as_view(), name='project-wallpost-detail'),
    url(r'^pmediawallposts/$', ProjectMediaWallPostList.as_view(), name='project-mediawallpost-list'),
    surl(r'^mediawallposts/<pk:#>$', ProjectMediaWallPostDetail.as_view(), name='project-mediawallpost-detail'),
    url(r'^textwallposts/$', ProjectTextWallPostList.as_view(), name='project-textwallpost-list'),
    surl(r'textwallposts/<pk:#>$', ProjectTextWallPostDetail.as_view(), name='project-textwallpost-detail'),
)

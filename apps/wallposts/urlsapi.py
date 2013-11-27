from apps.wallposts.views import WallPostDetail, TextWallPostList, MediaWallPostList, MediaWallPostPhotoList, MediaWallPostPhotoDetail
from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import ReactionList, ReactionDetail, WallPostList

urlpatterns = patterns('',
    url(r'^$', WallPostList.as_view(), name='wallpost-list'),
    surl(r'^<pk:#>$', WallPostDetail.as_view(), name='wallpost-detail'),

    url(r'^textwallposts/$', TextWallPostList.as_view(), name='text-wallpost-list'),
    url(r'^mediawallposts/$', MediaWallPostList.as_view(), name='media-wallpost-list'),

    url(r'^photos/$', MediaWallPostPhotoList.as_view(), name='mediawallpost-photo-list'),
    surl(r'^photos/<pk:#>$', MediaWallPostPhotoDetail.as_view(), name='mediawallpost-photo-list'),

    url(r'^reactions/$', ReactionList.as_view(), name='wallpost-reaction-list'),
    surl(r'^reactions/<pk:#>$', ReactionDetail.as_view(), name='wallpost-reaction-detail'),
)

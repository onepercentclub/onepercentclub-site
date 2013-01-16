from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import WallPostReactionList, WallPostReactionDetail, WallPostList

urlpatterns = patterns('',
    url(r'^$', WallPostList.as_view(), name='wallpost-reaction-list'),
    url(r'^reactions/$', WallPostReactionList.as_view(), name='wallpost-reaction-list'),
    surl(r'^reactions/<pk:#>$', WallPostReactionDetail.as_view(), name='wallpost-reaction-detail'),
)

from django.conf.urls.defaults import patterns

from surlex.dj import surl

from .views import (
    AlbumListView, AlbumDetailView, LocalPictureView, EmbeddedVideoView
)


urlpatterns = patterns('',
    # Album views
    surl(r'^$', AlbumListView.as_view(), name='album_list'),
    surl(r'^<slug:s>/$', AlbumDetailView.as_view(), name='album_detail'),

    # Media views
    surl(r'^<album_slug:s>/localpicture/<pk:#>/$',
         LocalPictureView.as_view(),
         name='localpicture_detail'
    ),
    surl(r'^<album_slug:s>/embeddedvideo/<pk:#>/$',
         EmbeddedVideoView.as_view(),
         name='embeddedvideo_detail'
    ),
)


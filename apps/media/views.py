from django.views.generic import ListView, DetailView

from .models import Album, LocalPicture, EmbeddedVideo


class AlbumViewBase(object):
    model = Album


class AlbumListView(AlbumViewBase, ListView):
    pass


class AlbumDetailView(AlbumViewBase, DetailView):
    pass


class MediaViewBase(DetailView):
    pass


class LocalPictureView(MediaViewBase):
    model = LocalPicture


class EmbeddedVideoView(MediaViewBase):
    model = EmbeddedVideo



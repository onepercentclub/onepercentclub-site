import logging
logger = logging.getLogger(__name__)

from django.contrib import admin

from sorl.thumbnail.admin import AdminImageMixin

from .models import Album, LocalPicture, EmbeddedVideo


class LocalPictureInline(AdminImageMixin, admin.StackedInline):
    model = LocalPicture

    # We won't be adding stuff here often, and should prevent to clutter up
    # the screen.
    extra = 0


class EmbeddedVideoInline(admin.StackedInline):
    model = EmbeddedVideo

    # We won't be adding stuff here often, and should prevent to clutter up
    # the screen.
    extra = 0


class AlbumAdmin(admin.ModelAdmin):
    model = Album

    inlines = [LocalPictureInline, EmbeddedVideoInline]

    search_fields = (
        'title', 'localpicture__title', 'embeddedvideo__title'
    )

    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Album, AlbumAdmin)

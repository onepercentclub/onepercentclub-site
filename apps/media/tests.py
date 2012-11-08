from django.test import TestCase
from django.core.exceptions import ValidationError

from apps.bluebottle_utils.tests import generate_random_slug

from .models import Album, LocalPicture, EmbeddedVideo


class MediaTestsMixin(object):
    """ Mixin class for the media app. """

    def create_album(self, slug=None):
        """ Create and return (but not save) an album. """

        if not slug:
            slug = generate_random_slug()
            while Album.objects.filter(slug=slug).exists():
                 slug = generate_random_slug()

        album = Album(slug=slug)
        return album

    def create_localpicture(self, album=None):
        """ Create and return (but not save) a local picture. """

        if not album:
            album = self.create_album()
            album.save()

        picture = LocalPicture(album=album)
        return picture

    def create_embeddedvideo(
        self, album=None, url='http://www.youtube.com/watch?v=54XHDUOHuzU'):
        """ Create an return (but not save) an embedded video. """

        if not album:
            album = self.create_album()
            album.save()

        video = EmbeddedVideo(album=album, url=url)
        return video


class SaveTests(TestCase, MediaTestsMixin):
    """ Tests for saving media. """

    def test_savealbum(self):
        """ Test whether saving an album works. """

        album = self.create_album()

        # Test whether unicode works
        self.assertTrue(unicode(album))

        # Save
        album.save()

    def test_savelocalpicture(self):
        """ Test whether saving a localpicture in an album works. """

        picture = self.create_localpicture()

        # Test whether unicode works
        self.assertTrue(unicode(picture))

        picture.save()

    def test_saveembeddedvideo(self):
        """ Test savind an embeddedvideo. """

        video = self.create_embeddedvideo()

        # Test whether unicode works
        self.assertTrue(unicode(video))

        video.save()

    def test_embeddedvideo_oembed(self):
        """ Test OEmbed functionality for video. """

        video = self.create_embeddedvideo()
        video.url = 'http://www.youtube.com/watch?v=54XHDUOHuzU'
        video.full_clean()
        video.save()

        video = EmbeddedVideo.objects.get(pk=video.pk)
        self.assertTrue(video.html)
        self.assertTrue(video.thumbnail_url)
        self.assertEquals(video.title, 'Future Crew - Second Reality demo - HD')

        # Test a fail
        video = self.create_embeddedvideo()
        video.url = 'http://www.youtube.com/watch?v=bnanana'
        self.assertRaises(ValidationError, video.full_clean)

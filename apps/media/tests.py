from django.test import TestCase
from django.core.urlresolvers import reverse

from .models import Album, LocalPicture, EmbeddedVideo


class MediaTestsMixin(object):
    """ Mixin class for the media app. """

    def create_album(self, slug='default'):
        """ Create and return (but not save) an album. """

        album = Album(slug=slug)
        return album

    def create_localpicture(self, album=None):
        """ Create and return (but not save) a local picture. """

        if not album:
            album = self.create_album()
            album.save()

        picture = LocalPicture(album=album)
        return picture

    def create_embeddedvideo(self, album=None):
        """ Create an return (but not save) an embedded video. """

        if not album:
            album = self.create_album()
            album.save()

        video = EmbeddedVideo(album=album)
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


class ViewTests(TestCase, MediaTestsMixin):
    """ Tests for media views. """

    def test_albumdetail(self):
        """ Test detail view for album. """
        album = self.create_album()
        album.save()

        picture = self.create_localpicture(album=album)
        picture.save()

        video = self.create_embeddedvideo(album=album)
        video.save()

        url = album.get_absolute_url()
        self.assertTrue(url)

        # The slug should be in the URL
        self.assertIn(album.slug, url)

        # Try and get the details
        response = self.client.get(url)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # The project title should be in the page, somewhere
        self.assertContains(response, album.title)

        self.assertContains(response, picture.get_absolute_url())
        self.assertContains(response, video.get_absolute_url())

    def test_localpicture(self):
        """ Test detail view for local picture. """

        picture = self.create_localpicture()
        picture.save()

        url = picture.get_absolute_url()
        self.assertTrue(url)

        # Try and get the details
        response = self.client.get(url)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

    def test_embeddedvideo(self):
        """ Test detail view for embedded video. """

        video = self.create_embeddedvideo()
        video.save()

        url = video.get_absolute_url()
        self.assertTrue(url)

        # Try and get the details
        response = self.client.get(url)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

    def test_albumlist(self):
        """ Test list view for album. """
        album1 = self.create_album()
        album1.save()

        album2 = self.create_album(slug='album2')
        album2.save()

        url = reverse('album_list')

        self.assertTrue(url)

        # Try and get the details
        response = self.client.get(url)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Titles and urls should be present
        self.assertContains(response, album1.title)
        # self.assertContains(response, album1.get_absolute_url())

        self.assertContains(response, album2.title)
        # self.assertContains(response, album2.get_absolute_url())

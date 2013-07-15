from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import six

from .middleware import RedirectFallbackMiddleware
from .models import Redirect


@override_settings(
    APPEND_SLASH=False,
    MIDDLEWARE_CLASSES=list(settings.MIDDLEWARE_CLASSES) +
        ['apps.redirects.middleware.RedirectFallbackMiddleware'],
    SITE_ID=1,
)
class RedirectTests(TestCase):

    def setUp(self):
        pass

    def test_model(self):
        r1 = Redirect.objects.create(
            old_path='/initial', new_path='/new_target')
        self.assertEqual(six.text_type(r1), "/initial ---> /new_target")

    def test_redirect(self):
        Redirect.objects.create(
            old_path='/initial', new_path='/new_target')
        response = self.client.get('/initial')
        self.assertRedirects(response,
            '/new_target', status_code=301, target_status_code=404)

    @override_settings(APPEND_SLASH=True)
    def test_redirect_with_append_slash(self):
        Redirect.objects.create(
            old_path='/initial/', new_path='/new_target/')
        response = self.client.get('/initial')
        self.assertRedirects(response,
            '/new_target/', status_code=301, target_status_code=404)

    @override_settings(APPEND_SLASH=True)
    def test_redirect_with_append_slash_and_query_string(self):
        Redirect.objects.create(
            old_path='/initial/?foo', new_path='/new_target/')
        response = self.client.get('/initial?foo')
        self.assertRedirects(response,
            '/new_target/', status_code=301, target_status_code=404)

    def test_regular_expression(self):
        Redirect.objects.create(
            old_path='/news/index/(\d+)/(.*)/',
            new_path='/my/news/$2/',
            regular_expression=True)
        response = self.client.get('/news/index/12345/foobar/')
        self.assertRedirects(response,
                             '/my/news/foobar/',
                             status_code=301, target_status_code=404)
        redirect = Redirect.objects.get(regular_expression=True)
        self.assertEqual(redirect.nr_times_visited, 1)

    def test_fallback_redirects(self):
        """
        Ensure redirects with fallback_redirect set are the last evaluated
        """
        Redirect.objects.create(
            old_path='/project/foo',
            new_path='/my/project/foo')
        
        Redirect.objects.create(
            old_path='/project/foo/(.*)',
            new_path='/my/project/foo/$1',
            regular_expression=True)

        Redirect.objects.create(
            old_path='/project/(.*)',
            new_path='/projects',
            regular_expression=True,
            fallback_redirect=True)

        Redirect.objects.create(
            old_path='/project/bar/(.*)',
            new_path='/my/project/bar/$1',
            regular_expression=True)

        Redirect.objects.create(
            old_path='/project/bar',
            new_path='/my/project/bar')

        response = self.client.get('/project/foo')
        self.assertRedirects(response,
                             '/my/project/foo',
                             status_code=301, target_status_code=404)

        response = self.client.get('/project/bar')
        self.assertRedirects(response,
                             '/my/project/bar',
                             status_code=301, target_status_code=404)

        response = self.client.get('/project/bar/details')
        self.assertRedirects(response,
                             '/my/project/bar/details',
                             status_code=301, target_status_code=404)

        response = self.client.get('/project/foobar')
        self.assertRedirects(response,
                             '/projects',
                             status_code=301, target_status_code=404)

        response = self.client.get('/project/foo/details')
        self.assertRedirects(response,
                             '/my/project/foo/details',
                             status_code=301, target_status_code=404)

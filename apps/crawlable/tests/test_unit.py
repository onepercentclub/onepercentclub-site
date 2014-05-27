import mock

from django.http import HttpResponse
from django.test import RequestFactory

from ..middleware import HASHBANG, ESCAPED_FRAGMENT, HashbangMiddleware
from onepercentclub.tests.utils import OnePercentTestCase


def escape_url(url):
    return url.replace(HASHBANG, '?%s=' % ESCAPED_FRAGMENT)


class HashbangMiddlewareTests(OnePercentTestCase):

    def setUp(self):
        self.init_projects()

        self.rf = RequestFactory()
        self.middleware = HashbangMiddleware()

        self.test_url = '/en/#!/projects'

    def test_middleware_with_hashbang(self):
        request = self.rf.get(self.test_url)
        result = self.middleware.process_request(request)

        self.assertIsNone(result)

    @mock.patch('apps.crawlable.middleware.WebCache.get_driver')
    def test_middleware_with_escaped_element(self, mock_get_driver):
        mock_get_driver.return_value = mock.MagicMock(page_source='<html><a href="%s">link</a></html>' % self.test_url)

        request = self.rf.get(escape_url(self.test_url))
        result = self.middleware.process_request(request)

        self.assertIsInstance(result, HttpResponse)
        self.assertContains(result, self.test_url)
        self.assertContains(result, 'Campaigns')


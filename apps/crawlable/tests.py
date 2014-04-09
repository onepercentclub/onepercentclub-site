from bluebottle.bb_projects.models import ProjectPhase
import mock

from django.http import HttpResponse
from django.test import TestCase, RequestFactory, LiveServerTestCase
from django.test.utils import override_settings
from django.utils.text import slugify

from apps.projects.tests import ProjectTestsMixin
from .middleware import HASHBANG, ESCAPED_FRAGMENT, HashbangMiddleware


def escape_url(url):
    return url.replace(HASHBANG, '?%s=' % ESCAPED_FRAGMENT)


class HashbangMiddlewareTests(TestCase):
    def setUp(self):
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

        self.assertEqual(mock_get_driver.call_count, 1)


class CrawlableTests(ProjectTestsMixin, LiveServerTestCase):
    """
    Tests one of the most complex pages, project list, with and without escaped fragments.
    """
    def setUp(self):
        self.projects = dict([(slugify(title), title) for title in [
            u'Women first', u'Mobile payments for everyone!', u'Schools for children '
        ]])

        for slug, title in self.projects.items():
            project = self.create_project(title=title, slug=slug)

            project.projectplan = ProjectPlan(title=project.title)
            project.projectplan.status = 'approved'
            project.projectplan.save()

            project.phase = ProjectPhase.objects.get(slug="campaign")
            project.save()

        self.project_url = '%s/en/#!/projects' % self.live_server_url
        self.client = self.client_class(SERVER_NAME=self.server_thread.host, SERVER_PORT=self.server_thread.port)

    def tearDown(self):
        from .middleware import web_cache

        if web_cache._web_driver:
            web_cache._web_driver.service.stop()

    def test_project_list_via_hashbang(self):
        response = self.client.get(self.project_url)

        for slug, title in self.projects.items():
            self.assertNotContains(response, title)


from bluebottle.bb_projects.models import ProjectPhase
from django.utils.text import slugify

from ..middleware import HASHBANG, ESCAPED_FRAGMENT
from onepercentclub.tests.factory_models.project_factories import OnePercentProjectFactory
from onepercentclub.tests.utils import OnePercentSeleniumTestCase


def escape_url(url):
    return url.replace(HASHBANG, '?%s=' % ESCAPED_FRAGMENT)


class CrawlableTests(OnePercentSeleniumTestCase):
    """
    Tests one of the most complex pages, project list, with and without escaped fragments.
    """
    def setUp(self):
        self.init_projects()

        self.projects = dict([(slugify(title), title) for title in [
            u'Women first', u'Mobile payments for everyone!', u'Schools for children '
        ]])

        for slug, title in self.projects.items():
            project = OnePercentProjectFactory.create(title=title, slug=slug)
            project.status = ProjectPhase.objects.get(slug="campaign")
            project.save()
            self.some_project = project

        self.project_list_url = '{0}/en/?_escaped_fragment_=/projects'.format(self.live_server_url)
        self.project_url = '{0}/en/?_escaped_fragment_=/projects/{1}'.format(self.live_server_url, self.some_project.slug)

        self.crawl_client = self.client_class(SERVER_NAME=self.server_thread.host, SERVER_PORT=self.server_thread.port)

    def test_project_list_via_hashbang(self):
        print "loading " + self.project_list_url
        response = self.crawl_client.get(self.project_list_url)

        for slug, title in self.projects.items():
            self.assertContains(response, title)

    def test_project_via_hashbang(self):
        print "loading " + self.project_url
        response = self.crawl_client.get(self.project_url)
        self.assertContains(response, self.some_project.title)

    def test_project_via_hashbang_with_query_params(self):
        response = self.crawl_client.get(self.project_url + '?x=12&y=100')
        self.assertContains(response, self.some_project.title)

    def test_project_via_hashbang_with_camel_case(self):
        response = self.crawl_client.get(self.project_list_url + '/Schools-For-Children')
        self.assertRedirects(response, self.project_url, status_code=301)

    def test_non_existing_project(self):
        # Non existing project should redirect to project list
        response = self.crawl_client.get(self.project_list_url + '/this-is-not-a-project')
        self.assertRedirects(response, self.project_list_url, status_code=301)

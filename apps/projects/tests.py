from django.test import TestCase

from apps.bluebottle_utils.tests import UserTestsMixin
from apps.organizations.tests import OrganiationTestsMixin

from .models import Project


class ProjectTestsMixin(OrganiationTestsMixin, UserTestsMixin):
    """ Mixin base class for tests using projects. """

    def create_project(self, organization=None, owner=None, title='',
                       slug=''):
        """
        Create a 'default' project with some standard values so it can be
        saved to the database, but allow for overriding.

        The returned object is not yet saved to the database.
        """

        if not organization:
            organization = self.create_organization()
            organization.save()

        if not owner:
            # Create a new user with a random username
            owner = self.create_user()

        project = Project(
            organization=organization, owner=owner, title=title, slug=slug
        )

        return project


class ProjectTests(TestCase, ProjectTestsMixin):
    """ Tests for projcts. """

    def setUp(self):
        """ Every test in this suite requires a project. """
        self.project = self.create_project(
            title='Banana Project',
            slug='banana'
        )
        self.project.save()

    def test_detailview(self):
        """ Test whether requesting of a project detail view works. """

        url = self.project.get_absolute_url()

        self.assertTrue(url)

        # The project slug should be in the URL
        self.assertIn(self.project.slug, url)

        # Try and get the details
        response = self.client.get(url)

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # The project title should be in the page, somewhere
        self.assertContains(response, self.project.title)


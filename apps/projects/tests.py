from decimal import Decimal

from django.test import TestCase

from apps.bluebottle_utils.tests import UserTestsMixin, generate_slug
from apps.organizations.tests import OrganizationTestsMixin

from .models import Project, PlanPhase


class ProjectTestsMixin(OrganizationTestsMixin, UserTestsMixin):
    """ Mixin base class for tests using projects. """

    def create_project(self, organization=None, owner=None, title='',
                       slug='', latitude=None, longitude=None):
        """
        Create a 'default' project with some standard values so it can be
        saved to the database, but allow for overriding.

        The returned object is not yet saved to the database.
        """

        if not latitude:
            latitude = Decimal('-11.2352')

        if not longitude:
            longitude = Decimal('-84.123')

        if not organization:
            organization = self.create_organization()
            organization.save()

        if not owner:
            # Create a new user with a random username
            owner = self.create_user()

        if not slug:
            slug = generate_slug()
            while Project.objects.filter(slug=slug).exists():
                 slug = generate_slug()

        project = Project(
            organization=organization, owner=owner, title=title, slug=slug,
            latitude=latitude, longitude=longitude
        )

        return project


class PlanPhaseTestMixin(object):
    def create_planphase(self, project, money_total=15000, money_asked=5000):
        """ Create (but not save) a plan phase. """
        planphase = PlanPhase(
            project=project, money_total=money_total, money_asked=money_asked
        )

        return planphase



class ProjectTests(TestCase, ProjectTestsMixin, PlanPhaseTestMixin):
    """ Tests for projects. """

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

        self.assertContains(response, self.project.owner)

    def test_amounts(self):
        """ Test calculation of donation amounts """

        phase = self.create_planphase(self.project, 12000, 3520)
        phase.save()

        self.assertEquals(self.project.money_asked(), 3520)

        self.project.donated = 2155

        self.assertEquals(self.project.money_donated(), 2155)

        self.project.donated = 2715.3

        self.assertEquals(self.project.money_donated(), 2715)

        self.project.donated = 1322.8

        self.assertEquals(self.project.money_donated(), 1322)

        self.project.donated = 2312
        self.project.planphase.money_asked = 3500

        self.assertEquals(self.project.money_needed(), 1188)

from decimal import Decimal
from datetime import timedelta
from apps.projects.views import ProjectRoot, ProjectInstance

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils import timezone

from apps.bluebottle_utils.tests import UserTestsMixin, generate_slug
from apps.organizations.tests import OrganizationTestsMixin
from apps.media.tests import MediaTestsMixin

from .models import Project, IdeaPhase, FundPhase, ActPhase, ResultsPhase, AbstractPhase


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


class FundPhaseTestMixin(object):
    def create_fundphase(self, project, budget_total=15000, money_asked=5000):
        """ Create (but not save) a fund phase. """
        fundphase = FundPhase()
        fundphase.project = project
        fundphase.budget_total = budget_total
        fundphase.money_asked = money_asked
        fundphase.startdate = timezone.now().date()
        return fundphase


class ProjectTests(TestCase, ProjectTestsMixin, FundPhaseTestMixin,
                   MediaTestsMixin):
    """ Tests for projects. """

    def setUp(self):
        """ Every test in this suite requires a project. """
        self.project = self.create_project(title='Banana Project',
                                           slug='banana')
        self.project.save()

    def test_amounts(self):
        """ Test calculation of donation amounts """

        phase = self.create_fundphase(self.project, 12000, 3520)
        phase.save()

        self.assertEquals(self.project.money_asked, 3520)

        self.project.fundphase.money_donated = 2155

        self.assertEquals(self.project.money_donated, 2155)

        self.project.fundphase.money_donated = 2715.3

        self.assertEquals(self.project.money_donated, 2715.3)

        self.project.fundphase.money_donated = 1322.8

        self.assertEquals(self.project.money_donated, 1322.8)

    def test_money_donated_default(self):
        """
        Tests for the default value of money_donated.
        """

        # Saving a new phase should have money_donated set to 0.
        phase = self.create_fundphase(self.project)
        phase.save()
        self.assertEquals(phase.money_donated, 0)

        # Saving the phase again with money_donated set shouldn't it back to 0.
        phase.money_donated = 10
        phase.save()
        self.assertNotEqual(phase.money_donated, 0)

        # Saving a phase with money_donated set before save() shouldn't set it to 0.
        funProject = self.create_project(title='Fun Project')
        funProject.save()
        phase = self.create_fundphase(funProject)
        phase.money_donated = 20
        phase.save()
        self.assertNotEqual(phase.money_donated, 0)

    def test_phase_dates_sync(self):
        """
        Tests that the auto-sync phase start / end date code works.
        """
        today = timezone.now().date()
        two_days_timedelta = timedelta(days=2)
        one_week_timedelta = timedelta(weeks=1)

        # Basic test for the auto-setting previous enddate.
        ideaphase = IdeaPhase(project=self.project)
        ideaphase.startdate = today
        ideaphase.save()
        fundphase = self.create_fundphase(self.project)
        fundphase.save()

        # Refresh the data and test:
        ideaphase = IdeaPhase.objects.get(id=ideaphase.id)
        self.assertTrue(fundphase.startdate == ideaphase.enddate)


        # Tests that previous phase start date is adjusted when the previous
        # phase end date is eariler than the previous phase start date.
        fundphase.startdate = today - two_days_timedelta
        fundphase.save()

        # Refresh the data and test:
        ideaphase = IdeaPhase.objects.get(id=ideaphase.id)
        self.assertTrue(fundphase.startdate == ideaphase.enddate)


        # Test for the auto-setting next startdate.
        resultsphase = ResultsPhase(project=self.project)
        resultsphase.startdate = today + two_days_timedelta
        resultsphase.save()
        actphase = ActPhase(project=self.project)
        actphase.startdate = today
        actphase.enddate = today + one_week_timedelta
        actphase.save()

        # Refresh the data and test:
        resultsphase = ResultsPhase.objects.get(id=resultsphase.id)
        self.assertTrue(resultsphase.startdate == actphase.enddate)

        # Tests that next phase end date is adjusted when the next phase start
        # date is later than the next phase end date.
        actphase = ActPhase.objects.get(id=actphase.id)
        fundphase = FundPhase.objects.get(id=fundphase.id)

        # The current state of things:
        self.assertEquals(fundphase.startdate, today - two_days_timedelta)
        self.assertEquals(fundphase.enddate, today)
        self.assertEquals(actphase.startdate, fundphase.enddate) # today
        self.assertEquals(actphase.enddate, today + one_week_timedelta)

        # Change the fund phase end date to be later than act phase end date.
        fundphase.enddate = today + timedelta(weeks=2)
        fundphase.save()

        # Refresh the data and test:
        actphase = ActPhase.objects.get(id=actphase.id)
        self.assertEquals(fundphase.enddate, actphase.startdate)
        # This is the important test.
        self.assertEquals(actphase.enddate, actphase.startdate)


        # Final refresh and tests:
        ideaphase = IdeaPhase.objects.get(id=ideaphase.id)
        fundphase = FundPhase.objects.get(id=fundphase.id)
        actphase = ActPhase.objects.get(id=actphase.id)
        resultsphase = ResultsPhase.objects.get(id=resultsphase.id)
        self.assertTrue(ideaphase.enddate == fundphase.startdate)
        self.assertTrue(fundphase.enddate == actphase.startdate)
        self.assertTrue(actphase.enddate == resultsphase.startdate)

    def test_phase_validation(self):
        """
        Tests that the phase validation is working.
        """

        # Setup sample phase.
        phase = self.create_fundphase(self.project)
        phase.startdate = timezone.now().date()
        phase.status = AbstractPhase.PhaseStatuses.progress
        phase.save()

        # Check that the validation error is raised.
        phase.enddate =  timezone.now().date() - timedelta(weeks=2)
        self.assertRaises(ValidationError, phase.full_clean)

        # Set a correct value and confirm there's no problem.
        phase.enddate =  timezone.now().date() + timedelta(weeks=2)
        phase.full_clean()
        phase.save()


# RequestFactory used for integration tests.
factory = RequestFactory()


class ProjectApiIntegrationTest(FundPhaseTestMixin, ProjectTestsMixin, TestCase):
    """
    Integration tests for the Project API.
    """

    def setUp(self):
        """
        Create 26 Project instances.
        """
        for char in 'abcdefghijklmnopqrstuvwxyz':
            project = self.create_project(title=char * 3, slug=char * 3)
            project.save()
            if ord(char) % 2 == 1:
                # Put half of the projects are in the fund phase.
                fundphase = self.create_fundphase(project)
                fundphase.save()
                project.phase = Project.ProjectPhases.fund
                project.save()

        self.root_view = ProjectRoot.as_view()
        self.instance_view = ProjectInstance.as_view()
        self.api_base = '/i18n/projects/'

    def test_drf2_root_view(self):
        """
        Tests for Project Root view. These basic tests are here because Project
        is the first API to use DRF2 and DRF2 hasn't been released yet. Not all
        DRF views need thorough integration testing like this.
        """

        # Basic test of DRF2.
        request = factory.get(self.api_base)
        response = self.root_view(request).render()
        self.assertEquals(response.status_code, 200)  # HTTP 200 - OK
        self.assertEquals(response.data['count'], 26)
        self.assertEquals(len(response.data['results']), 4)
        self.assertNotEquals(response.data['next'], None)
        self.assertEquals(response.data['previous'], None)

        # Tests that the next link works.
        request = factory.get(response.data['next'])
        response = self.root_view(request).render()
        self.assertEquals(response.status_code, 200)  # HTTP 200 - OK
        self.assertEquals(response.data['count'], 26)
        self.assertEquals(len(response.data['results']), 4)
        self.assertNotEquals(response.data['next'], None)
        self.assertNotEquals(response.data['previous'], None)

        # Tests that the previous link works.
        request = factory.get(response.data['previous'])
        response = self.root_view(request).render()
        self.assertEquals(response.status_code, 200)  # HTTP 200 - OK
        self.assertEquals(response.data['count'], 26)
        self.assertEquals(len(response.data['results']), 4)
        self.assertNotEquals(response.data['next'], None)
        self.assertEquals(response.data['previous'], None)

        # Tests that the last page works.
        request = factory.get(self.api_base + '?page=7')
        response = self.root_view(request).render()
        self.assertEquals(response.status_code, 200)  # HTTP 200 - OK
        self.assertEquals(response.data['count'], 26)
        self.assertEquals(len(response.data['results']), 2)
        self.assertEquals(response.data['next'], None)
        self.assertNotEquals(response.data['previous'], None)

        # Tests that the previous link from the last page works.
        request = factory.get(response.data['previous'])
        response = self.root_view(request).render()
        self.assertEquals(response.status_code, 200)  # HTTP 200 - OK
        self.assertEquals(response.data['count'], 26)
        self.assertEquals(len(response.data['results']), 4)
        self.assertNotEquals(response.data['next'], None)
        self.assertNotEquals(response.data['previous'], None)


    def test_drf2_root_view_query_filters(self):
        """
        Tests for Project Root view with filters. These basic tests are here
        because Project is the first API to use DRF2 and DRF2 hasn't been
        released yet. Not all DRF views need thorough integration testing like
        this.
        """

        # Tests that the phase filter works.
        request = factory.get(self.api_base + '?phase=fund')
        response = self.root_view(request).render()
        self.assertEquals(response.status_code, 200)  # HTTP 200 - OK
        self.assertEquals(response.data['count'], 13)
        self.assertEquals(len(response.data['results']), 4)
        self.assertNotEquals(response.data['next'], None)
        self.assertEquals(response.data['previous'], None)

        # Tests that the next link works with a filter.
        request = factory.get(response.data['next'])
        response = self.root_view(request).render()
        self.assertEquals(response.status_code, 200)  # HTTP 200 - OK
        self.assertEquals(response.data['count'], 13)
        self.assertEquals(len(response.data['results']), 4)
        self.assertNotEquals(response.data['next'], None)
        self.assertNotEquals(response.data['previous'], None)

        # Tests that the previous link works with a filter.
        request = factory.get(response.data['previous'])
        response = self.root_view(request).render()
        self.assertEquals(response.status_code, 200)  # HTTP 200 - OK
        self.assertEquals(response.data['count'], 13)
        self.assertEquals(len(response.data['results']), 4)
        self.assertNotEquals(response.data['next'], None)
        self.assertEquals(response.data['previous'], None)

        # Tests that the last page works with a filter.
        request = factory.get(self.api_base + '?page=4&phase=fund')
        response = self.root_view(request).render()
        self.assertEquals(response.status_code, 200)  # HTTP 200 - OK
        self.assertEquals(response.data['count'], 13)
        self.assertEquals(len(response.data['results']), 1)
        self.assertEquals(response.data['next'], None)
        self.assertNotEquals(response.data['previous'], None)

        # Tests that the previous link from the last page works with a filter.
        request = factory.get(response.data['previous'])
        response = self.root_view(request).render()
        self.assertEquals(response.status_code, 200)  # HTTP 200 - OK
        self.assertEquals(response.data['count'], 13)
        self.assertEquals(len(response.data['results']), 4)
        self.assertNotEquals(response.data['next'], None)
        self.assertNotEquals(response.data['previous'], None)

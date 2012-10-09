from decimal import Decimal
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
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
        fundphase = FundPhase(
            project=project, budget_total=budget_total, money_asked=money_asked
        )

        return fundphase


class ProjectTests(TestCase, ProjectTestsMixin, FundPhaseTestMixin,
                   MediaTestsMixin):
    """ Tests for projects. """

    def setUp(self):
        """ Every test in this suite requires a project. """
        self.project = self.create_project(
            title='Banana Project',
            slug='banana'
        )
        self.project.save()

    def test_amounts(self):
        """ Test calculation of donation amounts """

        phase = self.create_fundphase(self.project, 12000, 3520)
        phase.startdate = timezone.now().date()
        phase.save()

        self.assertEquals(self.project.money_asked(), 3520)

        self.project.fundphase.money_donated = 2155

        self.assertEquals(self.project.money_donated(), 2155)

        self.project.fundphase.money_donated = 2715.3

        self.assertEquals(self.project.money_donated(), 2715)

        self.project.fundphase.money_donated = 1322.8

        self.assertEquals(self.project.money_donated(), 1322)

        self.project.fundphase.money_donated = 2312
        self.project.fundphase.money_asked = 3500

        self.assertEquals(self.project.money_needed(), 1188)

    def test_money_donated_default(self):
        """
        Tests for the default value of money_donated.
        """

        # Saving a new phase should have money_donated set to 0.
        phase = self.create_fundphase(self.project)
        phase.startdate = timezone.now().date()
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
        phase.startdate = timezone.now().date()
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
        fundphase.startdate = today
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


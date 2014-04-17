from django.test import TestCase

from bluebottle.test.factory_models.accounts import BlueBottleUserFactory
from bluebottle.test.factory_models.projects import ProjectThemeFactory, ProjectPhaseFactory
from bluebottle.utils.utils import get_project_model

from ..tests.factory_models.project_factories import OnePercentProjectFactory

from apps.fund.models import DonationStatuses, Donation, Order

PROJECT_MODEL = get_project_model()

class CalculateProjectMoneyDonatedTest(TestCase):

    def setUp(self):
        # Required by Project model save method
        self.phase = ProjectPhaseFactory.create(sequence=1, name='Plan - New')

        self.some_project = OnePercentProjectFactory.create(amount_asked=5000)
        self.another_project = OnePercentProjectFactory.create(amount_asked=5000)

        self.some_user = BlueBottleUserFactory.create()
        self.another_user = BlueBottleUserFactory.create()

    def test_donated_amount(self):
        # Some project have amount_asked of 5000000 (cents that is)
        self.assertEqual(self.some_project.amount_asked, 5000)

        # A project without donations should have amount_donated of 0
        self.assertEqual(self.some_project.amount_donated, 0)

        # Create a new donation of 15 in status 'new'. project money donated should be 0
        first_donation = self._create_donation(user=self.some_user, project=self.some_project, amount=1500,
                                               status=DonationStatuses.new)
        self.assertEqual(self.some_project.amount_donated, 0)


        # Create a new donation of 25 in status 'in_progress'. project money donated should be 0.
        second_donation = self._create_donation(user=self.some_user, project=self.some_project, amount=2500,
                                                status=DonationStatuses.in_progress)
        self.assertEqual(self.some_project.amount_donated, 0)

        # Setting the first donation to status 'paid' money donated should be 1500
        first_donation.status = DonationStatuses.paid
        first_donation.save()
        self.assertEqual(self.some_project.amount_donated, 1500)

        # Setting the second donation to status 'pending' money donated should be 40
        second_donation.status = DonationStatuses.pending
        second_donation.save()
        self.assertEqual(self.some_project.amount_donated, 4000)

    def _create_donation(self, user=None, amount=None, project=None, status=DonationStatuses.new):
        """ Helper method for creating donations."""
        if not project:
            project = OnePercentProjectFactory.create()
            project.save()

        if not user:
            user = BlueBottleUserFactory.create()

        if not amount:
            amount = Decimal('10.00')

        order = Order.objects.create()
        donation = Donation.objects.create(user=user, amount=amount, status=status, project=project, order=order)

        return donation


class ProjectPhaseLoggerTest(TestCase):
    def setUp(self):
        self.some_project = OnePercentProjectFactory.create()

    def test_phase_change_logged(self):
        # One phase should be logged due to creation of the project
        self.assertEqual(1, self.some_project.projectphaselog_set.count())

        # change the phase, it should be logged
        self.some_project.phase = ProjectPhases.plan
        self.some_project.save()

        self.assertEqual(2, self.some_project.projectphaselog_set.count())


class FailedProjectTest(TestCase):
    """ Verify that the project is marked as failed when pitch/plan is rejected """
    def setUp(self):
        self.some_project = OnePercentProjectFactory.create(phase='plan')

    def test_pitch_rejected(self):
        self.some_project.projectpitch.status = ProjectPitch.PitchStatuses.rejected
        self.some_project.projectpitch.save()
        self.assertEqual(self.some_project.phase, ProjectPhases.failed)


    def test_plan_rejected(self):
        self.some_project.projectplan.status = ProjectPlan.PlanStatuses.rejected
        self.some_project.projectplan.save()

        self.assertEqual(self.some_project.phase, ProjectPhases.failed)

from decimal import Decimal

from django.test import TestCase

from django_dynamic_fixture import N, G

from apps.projects.models import (
    Project, ProjectPhases, ProjectCampaign, ProjectPlan
)
from apps.fund.models import Donation, DonationStatuses
from .models import Payout


class PayoutTestCase(TestCase):
    """ Testcase for Payouts. """

    def setUp(self):
        """ Setup a project ready for payout. """
        self.project = G(
            Project
        )

        self.campaign = G(
            ProjectCampaign,
            project=self.project,
            money_asked=1500
        )

        self.projectplan = G(
            ProjectPlan,
            project=self.project
        )

        # Update phase to campaign.
        self.project.phase = ProjectPhases.campaign
        self.project.save()

        self.donation = G(
            Donation,
            project=self.project,
            voucher=None,
            donation_type=Donation.DonationTypes.one_off,
            amount=1500
        )

    def test_save(self):
        """ Test saving a payout. """

        # Generate new payout
        payout = N(Payout)

        # Save it
        payout.save()

    def test_create_payout(self):
        """
        Test automatically generating a payout.
        """

        # No payouts should exist yet as project is not in act phase yet
        self.assertFalse(Payout.objects.exists())

        # Set status of donation to paid
        self.donation.status = DonationStatuses.paid
        self.donation.save()

        # Update campaign donations
        self.campaign.update_money_donated()

        # Update phase to act.
        self.project.phase = ProjectPhases.act
        self.project.save()

        # Payout should have been created
        self.assertEquals(Payout.objects.count(), 1)

        payout = Payout.objects.all()[0]

        # Check the project and the amount
        self.assertEquals(payout.project, self.project)
        self.assertEquals(payout.amount, Decimal('14.25'))

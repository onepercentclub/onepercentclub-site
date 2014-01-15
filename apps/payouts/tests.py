from decimal import Decimal

from django.test import TestCase

from django_dynamic_fixture import N, G

from apps.projects.models import (
    Project, ProjectPhases, ProjectCampaign, ProjectPlan
)
from apps.fund.models import Donation, DonationStatuses

from .models import Payout
from .choices import PayoutRules


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

    def test_unicode(self):
        """ Test unicode() on payout. """

        payout = G(Payout)
        self.assertTrue(unicode(payout))

    def test_create_payout(self):
        """
        Test automatically generating a payout.
        """

        # No payouts should exist yet as project is not in act phase yet
        self.assertFalse(Payout.objects.exists())

        # Set status of donation to pending
        self.donation.status = DonationStatuses.pending
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
        self.assertEquals(payout.amount_raised, Decimal('15.00'))

    def test_invoice_reference(self):
        """ Test generating invoice_reference. """
        # Set status of donation to paid
        self.donation.status = DonationStatuses.pending
        self.donation.save()

        # Update campaign donations
        self.campaign.update_money_donated()

        # Update phase to act.
        self.project.phase = ProjectPhases.act
        self.project.save()

        # Fetch payout
        payout = Payout.objects.all()[0]

        self.assertIn(str(self.project.id), payout.invoice_reference)
        self.assertIn(str(payout.id), payout.invoice_reference)

    def test_create_payment_rule_five(self):
        """ Fully funded projects should get payment rule five. """

        # Set status of donation to paid
        self.donation.status = DonationStatuses.paid
        self.donation.save()

        # Update campaign donations
        self.campaign.update_money_donated()

        # Update phase to act.
        self.project.phase = ProjectPhases.act
        self.project.save()

        payout = Payout.objects.all()[0]
        self.assertEquals(payout.payout_rule, PayoutRules.five)
        self.assertEquals(payout.organization_fee, Decimal('0.75'))
        self.assertEquals(payout.amount_payable, Decimal('14.25'))

    def test_create_payment_rule_twelve(self):
        """ Not fully funded projects should get payment rule twelve. """

        # Set status of donation to paid
        self.donation.amount = 1400
        self.donation.status = DonationStatuses.paid
        self.donation.save()

        # Update campaign donations
        self.campaign.update_money_donated()

        # Update phase to act.
        self.project.phase = ProjectPhases.act
        self.project.save()

        payout = Payout.objects.all()[0]
        self.assertEquals(payout.payout_rule, PayoutRules.twelve)
        self.assertEquals(payout.organization_fee, Decimal('1.68'))
        self.assertEquals(payout.amount_payable, Decimal('12.32'))

    def test_safe_amount_new(self):
        """ Test safe_amount_payable for new donations. """

        # Set status of donation to paid
        self.donation.status = DonationStatuses.new
        self.donation.save()

        # Update campaign donations
        self.campaign.update_money_donated()

        # Update phase to act.
        self.project.phase = ProjectPhases.act
        self.project.save()

        # Fetch payout
        payout = Payout.objects.all()[0]

        # No money is even pending
        self.assertEquals(payout.amount_payable, Decimal('0.00'))
        self.assertEquals(payout.safe_amount_payable, Decimal('0.00'))

    def test_safe_amount_pending(self):
        """ Test safe_amount_payable for pending donations. """

        # Set status of donation to paid
        self.donation.status = DonationStatuses.pending
        self.donation.save()

        # Update campaign donations
        self.campaign.update_money_donated()

        # Update phase to act.
        self.project.phase = ProjectPhases.act
        self.project.save()

        # Fetch payout
        payout = Payout.objects.all()[0]

        # No money is even pending
        self.assertEquals(payout.amount_payable, Decimal('14.25'))
        self.assertEquals(payout.safe_amount_payable, Decimal('0.00'))

    def test_safe_amount_paid(self):
        """ Test safe_amount_payable for paid donations. """

        # Set status of donation to paid
        self.donation.status = DonationStatuses.paid
        self.donation.save()

        # Update campaign donations
        self.campaign.update_money_donated()

        # Update phase to act.
        self.project.phase = ProjectPhases.act
        self.project.save()

        # Fetch payout
        payout = Payout.objects.all()[0]

        # No money is safe - just yet
        self.assertEquals(payout.amount_payable, Decimal('14.25'))
        self.assertEquals(payout.safe_amount_payable, Decimal('14.25'))



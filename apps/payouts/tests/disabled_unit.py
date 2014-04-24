import decimal
import datetime
from bluebottle.bb_projects.models import ProjectPhase

from django.test import TestCase

from django_dynamic_fixture import N, G

from apps.projects.models import Project

from apps.fund.models import Donation, DonationStatuses

from apps.cowry import factory
from apps.cowry.models import PaymentStatuses

from ..models import (
    Payout, PayoutLog, OrganizationPayout, OrganizationPayoutLog
)
from ..choices import PayoutRules, PayoutLineStatuses
from onepercentclub.tests.factory_models.donation_factories import DonationFactory
from onepercentclub.tests.factory_models.project_factories import OnePercentProjectFactory
from onepercentclub.tests.utils import OnePercentTestCase
from ..utils import date_timezone_aware


class PayoutTestCase(OnePercentTestCase):
    """ Testcase for Payouts. """

    def setUp(self):
        """ Setup a project ready for payout. """

        self.init_projects()

        self.project = OnePercentProjectFactory.create()

        # Update phase to campaign.
        self.project.status = ProjectPhase.objects.get(slug='campaign')
        self.project.save()

        self.donation = DonationFactory.create(
            project=self.project,
            voucher=None,
            donation_type=Donation.DonationTypes.one_off,
            amount=1500
        )

        super(PayoutTestCase, self).setUp()

    def test_save(self):
        """ Test saving a payout. """

        # Generate new payout
        payout = N(Payout, completed=None)

        # Validate
        payout.clean()

        # Save it
        payout.save()

    def test_unicode(self):
        """ Test unicode() on payout. """

        payout = G(Payout, completed=None)
        self.assertTrue(unicode(payout))

    def test_completed(self):
        """ Test the transition to completed. """

        payout = G(Payout, completed=None, status=PayoutLineStatuses.progress)
        payout.save()

        self.assertFalse(payout.completed)

        # Change status to completed
        payout.status = PayoutLineStatuses.completed
        payout.save()

        # Completed date should now be set
        self.assertTrue(payout.completed)

    def test_create_payout(self):
        """
        Test automatically generating a payout.
        """

        # No payouts should exist yet as project is not in act phase yet
        self.assertFalse(Payout.objects.exists())

        # Set status of donation to pending
        self.donation.status = DonationStatuses.pending
        self.donation.save()

        # Update phase to act.
        self.project.status = ProjectPhase.objects.get(slug='done-complete')
        self.project.save()

        # Payout should have been created
        self.assertEquals(Payout.objects.count(), 1)

        payout = Payout.objects.all()[0]

        # Check the project and the amount
        self.assertEquals(payout.project, self.project)
        self.assertEquals(payout.amount_raised, decimal.Decimal('15.00'))

    def test_invoice_reference(self):
        """ Test generating invoice_reference. """
        # Set status of donation to paid
        self.donation.status = DonationStatuses.pending
        self.donation.save()

        # Update phase to act.
        self.project.status = ProjectPhase.objects.get(slug='done-complete')
        self.project.save()

        # Fetch payout
        payout = Payout.objects.all()[0]

        self.assertIn(str(self.project.id), payout.invoice_reference)
        self.assertIn(str(payout.id), payout.invoice_reference)

    def test_create_payment_rule_five(self):
        """ Legacy projects should get payment rule five. """

        # Set status of donation to paid
        self.donation.status = DonationStatuses.paid
        self.donation.save()


        # Update phase to act.
        self.project.status = ProjectPhase.objects.get(slug='done-complete')
        self.project.save()

        payout = Payout.objects.all()[0]
        self.assertEquals(payout.payout_rule, PayoutRules.five)
        self.assertEquals(payout.organization_fee, decimal.Decimal('0.75'))
        self.assertEquals(payout.amount_payable, decimal.Decimal('14.25'))

    def test_create_payment_rule_seven(self):
        """ Fully funded projects should get payment rule seven. """

        # Set status of donation to paid
        self.donation.status = DonationStatuses.paid
        self.donation.save()


        # Update phase to act.
        self.project.status = ProjectPhase.objects.get(slug='done-complete')
        self.project.save()

        payout = Payout.objects.all()[0]
        self.assertEquals(payout.payout_rule, PayoutRules.seven)
        self.assertEquals(payout.organization_fee, decimal.Decimal('1.05'))
        self.assertEquals(payout.amount_payable, decimal.Decimal('13.95'))

    def test_create_payment_rule_twelve(self):
        """ Not fully funded projects should get payment rule twelve. """

        # Set status of donation to paid
        self.donation.amount = 1400
        self.donation.status = DonationStatuses.paid
        self.donation.save()

        # Update phase to act.
        self.project.status = ProjectPhase.objects.get(slug='done-complete')
        self.project.save()

        payout = Payout.objects.all()[0]
        self.assertEquals(payout.payout_rule, PayoutRules.twelve)
        self.assertEquals(payout.organization_fee, decimal.Decimal('1.68'))
        self.assertEquals(payout.amount_payable, decimal.Decimal('12.32'))

    def test_amounts_new(self):
        """ Test amounts for new donations. """

        # Set status of donation to paid
        self.donation.status = DonationStatuses.new
        self.donation.save()

        # Update phase to act.
        self.project.status = ProjectPhase.objects.get(slug='done-complete')
        self.project.save()

        # Fetch payout
        payout = Payout.objects.all()[0]

        # No money is even pending
        self.assertEquals(payout.amount_raised, decimal.Decimal('0.00'))
        self.assertEquals(payout.amount_payable, decimal.Decimal('0.00'))

        self.assertEquals(payout.get_amount_pending(), decimal.Decimal('0.00'))
        self.assertEquals(payout.get_amount_safe(), decimal.Decimal('0.00'))
        self.assertEquals(payout.get_amount_failed(), decimal.Decimal('0.00'))

    def test_amounts_pending(self):
        """ Test amounts for pending donations. """

        # Set status of donation
        self.donation.status = DonationStatuses.pending
        self.donation.save()

        # Update phase to act.
        self.project.status = ProjectPhase.objects.get(slug='done-complete')
        self.project.save()

        # Fetch payout
        payout = Payout.objects.all()[0]

        # Money is pending but not paid
        self.assertEquals(payout.amount_raised, decimal.Decimal('15.00'))
        self.assertEquals(payout.amount_payable, decimal.Decimal('13.95'))

        self.assertEquals(payout.get_amount_pending(), decimal.Decimal('15.00'))
        self.assertEquals(payout.get_amount_safe(), decimal.Decimal('0.00'))
        self.assertEquals(payout.get_amount_failed(), decimal.Decimal('0.00'))

    def test_amounts_failed(self):
        """
        Test amounts for pending donation changed into failed after creating payout.
        """

        # Set status of donation to pending first
        self.donation.status = DonationStatuses.pending
        self.donation.save()

        # Update phase to act.
        self.project.status = ProjectPhase.objects.get(slug='done-complete')
        self.project.save()

        # Set status of donation to failed
        self.donation.status = DonationStatuses.failed
        self.donation.save()

        # Fetch payout
        payout = Payout.objects.all()[0]

        # Saved amounts should be same as pending
        self.assertEquals(payout.amount_raised, decimal.Decimal('15.00'))
        self.assertEquals(payout.amount_payable, decimal.Decimal('13.95'))

        # Realtime amounts should be different
        self.assertEquals(payout.get_amount_pending(), decimal.Decimal('0.00'))
        self.assertEquals(payout.get_amount_safe(), decimal.Decimal('0.00'))
        self.assertEquals(payout.get_amount_failed(), decimal.Decimal('15.00'))

    def test_amounts_paid(self):
        """ Test amounts for paid donations. """

        # Set status of donation to paid
        self.donation.status = DonationStatuses.paid
        self.donation.save()

        # Update phase to act.
        self.project.status = ProjectPhase.objects.get(slug='done-complete')
        self.project.save()

        # Fetch payout
        payout = Payout.objects.all()[0]

        # Money is safe now, nothing's pending
        self.assertEquals(payout.amount_raised, decimal.Decimal('15.00'))
        self.assertEquals(payout.amount_payable, decimal.Decimal('13.95'))

        self.assertEquals(payout.get_amount_pending(), decimal.Decimal('0.00'))
        self.assertEquals(payout.get_amount_safe(), decimal.Decimal('15.00'))
        self.assertEquals(payout.get_amount_failed(), decimal.Decimal('0.00'))


class PayoutLogMixin(object):
    """
    Base class for testing payout logs for Payout and OrganizationPayout.
    """
    def setUp(self):
        self.payout = G(self.obj_class, status=PayoutLineStatuses.new, completed=None)

        super(PayoutLogMixin, self).setUp()

    def test_save(self):
        """ Test saving a PayoutLog. """

        # Generate new payout
        obj = N(self.log_class, payout=self.payout)

        # Validate
        obj.clean()

        # Save it
        obj.save()

    def test_initial(self):
        """ Test whether an initial self.log_class is created for payout """

        self.assertEquals(self.log_class.objects.count(), 1)

        payout_log = self.log_class.objects.all()[0]

        self.assertEquals(payout_log.payout, self.payout)
        self.assertEquals(payout_log.old_status, None)
        self.assertEquals(payout_log.new_status, self.payout.status)
        self.assertLessEqual(payout_log.date - self.payout.updated,
            datetime.timedelta(seconds=20))

    def test_update(self):
        """ Test whether a status update on payout updates log. """

        self.payout.status = PayoutLineStatuses.progress
        self.payout.save()

        self.assertEquals(self.log_class.objects.count(), 2)

        payout_log = self.payout.log_set.latest()

        self.assertEquals(payout_log.payout, self.payout)
        self.assertEquals(payout_log.old_status, PayoutLineStatuses.new)
        self.assertEquals(payout_log.new_status, PayoutLineStatuses.progress)
        self.assertLessEqual(payout_log.date - self.payout.updated,
            datetime.timedelta(seconds=20))


class PayoutLogTestCase(PayoutLogMixin, TestCase):
    """ Test case for PayoutLog. """

    obj_class = Payout
    log_class = PayoutLog


class OrganizationPayoutLogTestCase(PayoutLogMixin, TestCase):
    """ Test case for PayoutLog. """

    obj_class = OrganizationPayout
    log_class = OrganizationPayoutLog


class OrganizationPayoutTestCase(TestCase):
    """ Test case for OrganizationPayout. """

    def setUp(self):
        """ Setup reference to today. """

        self.today = datetime.datetime.now().date()

        super(OrganizationPayoutTestCase, self).setUp()

    def create_donation(self):
        """
        Helper method creating and returning a paid donation.
        """

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
            amount=1500,
            status=DonationStatuses.paid
        )

        self.order = self.donation.order

        return self.order

    def create_payment(self):
        """
        Helper method creating a payment (and donation and order) and setting
        the payment status to paid.
        """

        self.create_donation()

        # Source: apps.cowry_docdata.tests
        self.payment = factory.create_payment_object(
            self.order, 'dd-webmenu', amount=2000, currency='EUR')
        self.payment.country = 'NL'
        self.payment.city = 'Amsterdam'
        self.payment.address = 'Dam'
        self.payment.postal_code = '1001AM'
        self.payment.first_name = 'Nijntje'
        self.payment.last_name = 'het Konijntje'
        self.payment.email = 'nijntje@hetkonijntje.nl'
        self.payment.fee = 50
        self.payment.status = PaymentStatuses.paid
        self.payment.save()

        return self.payment

    def create_payout(self):
        """
        Helper method creating a completed Payout with organization fee
        of 0.75.
        """

        self.create_donation()

        # Progress to act phase, creating a Payout
        self.project.phase = ProjectPhases.act
        self.project.save()

        # Change payout status to complete
        self.payout = Payout.objects.all()[0]
        self.payout.status = PayoutLineStatuses.completed
        self.payout.save()

        return self.payout

    def test_save(self):
        """ Test saving a payout. """

        # Generate new payout
        payout = N(
            OrganizationPayout,
            completed=None,
            start_date=datetime.date(2013, 01, 01),
            end_date=datetime.date(2013, 01, 31)
        )

        # Validate
        payout.clean()

        # Save it
        payout.save()

    def test_unicode(self):
        """ Test unicode() on payout. """

        payout = G(OrganizationPayout, completed=None)
        self.assertTrue(unicode(payout))

    def test_completed(self):
        """ Test the transition to completed. """

        payout = G(
            OrganizationPayout, completed=None, status=PayoutLineStatuses.progress
        )
        payout.save()

        self.assertFalse(payout.completed)

        # Change status to completed
        payout.status = PayoutLineStatuses.completed
        payout.save()

        # Completed date should now be set
        self.assertTrue(payout.completed)

    def test_get_organization_fee(self):
        """ Test calculation of the organization fee from Payouts. """

        # Create a Payout to calculate organization fee over
        self.create_payout()

        # Generate an OrganizationPayout with period containing
        # the Payout's completed date
        org_payout = N(
            OrganizationPayout,
            completed=None,
            start_date=self.today - datetime.timedelta(days=1),
            end_date=self.today + datetime.timedelta(days=1)
        )

        # See whether the aggregate organization fee corresponds
        self.assertEquals(
            org_payout._get_organization_fee(), decimal.Decimal('1.05')
        )

    def test_get_psp_fee(self):
        """" Test calculation of PSP fees from Orders. """

        self.create_payment()

        # Generate an OrganizationPayout with period containing the payment's
        # creation date.
        org_payout = N(
            OrganizationPayout,
            completed=None,
            start_date=self.today - datetime.timedelta(days=1),
            end_date=self.today + datetime.timedelta(days=1)
        )

        self.assertEquals(
            org_payout._get_psp_fee(), decimal.Decimal('0.50')
        )

    def test_calculate_amounts(self):
        """ Test calculation of amounts. """

        # Create a Payout to calculate organization fee over
        self.create_payout()
        self.create_payment()

        # Generate an OrganizationPayout with period containing the payment's
        # creation date.
        org_payout = G(
            OrganizationPayout,
            completed=None,
            start_date=self.today - datetime.timedelta(days=1),
            end_date=self.today + datetime.timedelta(days=1)
        )

        self.assertEquals(
            org_payout.organization_fee_excl, decimal.Decimal('0.87')
        )

        self.assertEquals(
            org_payout.organization_fee_vat, decimal.Decimal('0.18')
        )

        self.assertEquals(
            org_payout.organization_fee_incl, decimal.Decimal('1.05')
        )

        self.assertEquals(
            org_payout.psp_fee_excl, decimal.Decimal('0.50')
        )

        self.assertEquals(
            org_payout.psp_fee_vat, decimal.Decimal('0.10')
        )

        self.assertEquals(
            org_payout.psp_fee_incl, decimal.Decimal('0.60')
        )

        self.assertEquals(
            org_payout.payable_amount_excl, decimal.Decimal('0.37')
        )

        self.assertEquals(
            org_payout.payable_amount_vat, decimal.Decimal('0.08')
        )

        self.assertEquals(
            org_payout.payable_amount_incl, decimal.Decimal('0.45')
        )

    def test_other_costs_excl(self):
        """ Test calculations for other costs excluding VAT. """

        # Create a Payout to calculate organization fee over
        self.create_payout()
        self.create_payment()

        # Generate an OrganizationPayout with period containing the payment's
        # creation date.
        org_payout = G(
            OrganizationPayout,
            completed=None,
            start_date=self.today - datetime.timedelta(days=1),
            end_date=self.today + datetime.timedelta(days=1)
        )

        org_payout.other_costs_excl = decimal.Decimal('1.00')

        org_payout.calculate_amounts()

        self.assertEquals(
            org_payout.other_costs_incl, decimal.Decimal('1.21')
        )

        self.assertEquals(
            org_payout.other_costs_vat, decimal.Decimal('0.21')
        )

    def test_other_costs_incl(self):
        """ Test calculations for other costs including VAT. """

        # Create a Payout to calculate organization fee over
        self.create_payout()
        self.create_payment()

        # Generate an OrganizationPayout with period containing the payment's
        # creation date.
        org_payout = G(
            OrganizationPayout,
            completed=None,
            start_date=self.today - datetime.timedelta(days=1),
            end_date=self.today + datetime.timedelta(days=1)
        )

        org_payout.other_costs_incl = decimal.Decimal('1.21')

        org_payout.calculate_amounts()

        self.assertEquals(
            org_payout.other_costs_excl, decimal.Decimal('1.00')
        )

        self.assertEquals(
            org_payout.other_costs_vat, decimal.Decimal('0.21')
        )

    def test_invoice_reference(self):
        """ Test generating invoice_reference. """

        org_payout = G(
            OrganizationPayout,
            completed=None, invoice_reference='',
            start_date=self.today - datetime.timedelta(days=1),
            end_date=self.today + datetime.timedelta(days=1)
        )

        self.assertIn(str(org_payout.id), org_payout.invoice_reference)
        self.assertIn(str(self.today.year), org_payout.invoice_reference)

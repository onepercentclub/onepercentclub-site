import decimal
import datetime
import doctest

from lxml import etree

from django.test import TestCase

from django_dynamic_fixture import N, G

from apps.projects.models import (
    Project, ProjectPhases, ProjectCampaign, ProjectPlan
)
from apps.fund.models import Donation, DonationStatuses

from apps.cowry import factory
from apps.cowry.models import PaymentStatuses

from apps.sepa.tests.base import SepaXMLTestMixin

from .models import Payout, OrganizationPayout
from .choices import PayoutRules, PayoutLineStatuses
from .utils import date_timezone_aware


class PayoutTestCase(SepaXMLTestMixin, TestCase):
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
        self.assertEquals(payout.amount_raised, decimal.Decimal('15.00'))

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
        """ Legacy projects should get payment rule five. """

        # Use date before 2014-1-1
        self.campaign.created = date_timezone_aware(datetime.date(2013, 1, 1))

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
        self.assertEquals(payout.organization_fee, decimal.Decimal('0.75'))
        self.assertEquals(payout.amount_payable, decimal.Decimal('14.25'))

    def test_create_payment_rule_seven(self):
        """ Fully funded projects should get payment rule seven. """

        # Set status of donation to paid
        self.donation.status = DonationStatuses.paid
        self.donation.save()

        # Update campaign donations
        self.campaign.update_money_donated()

        # Update phase to act.
        self.project.phase = ProjectPhases.act
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

        # Update campaign donations
        self.campaign.update_money_donated()

        # Update phase to act.
        self.project.phase = ProjectPhases.act
        self.project.save()

        payout = Payout.objects.all()[0]
        self.assertEquals(payout.payout_rule, PayoutRules.twelve)
        self.assertEquals(payout.organization_fee, decimal.Decimal('1.68'))
        self.assertEquals(payout.amount_payable, decimal.Decimal('12.32'))

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
        self.assertEquals(payout.amount_payable, decimal.Decimal('0.00'))
        self.assertEquals(payout.safe_amount_payable, decimal.Decimal('0.00'))

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
        self.assertEquals(payout.amount_payable, decimal.Decimal('13.95'))
        self.assertEquals(payout.safe_amount_payable, decimal.Decimal('0.00'))

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
        self.assertEquals(payout.amount_payable, decimal.Decimal('13.95'))
        self.assertEquals(payout.safe_amount_payable, decimal.Decimal('13.95'))

    def test_create_sepa_xml(self):
        """ Smoketest creation of SEPA XML. """

        # Setup organization
        organization = self.project.projectplan.organization
        organization.account_name = 'Funny organization'
        organization.account_iban = 'NL90ABNA0111111111'
        organization.account_bic = 'ABNANL2A'
        organization.save()

        # Set status of donation to paid
        self.donation.status = DonationStatuses.paid
        self.donation.save()

        # Update campaign donations
        self.campaign.update_money_donated()

        # Update phase to act.
        self.project.phase = ProjectPhases.act
        self.project.save()

        # Generate XML
        xml = Payout.create_sepa_xml(Payout.objects.all())

        tree = etree.XML(xml)
        self.xmlschema.assertValid(tree)

        # Test content
        main = tree[0]
        header = main[0]

        # Number of transactions
        self.assertEqual(header[2].text, "1")

        # Total amount
        self.assertEqual(header[3].text, '13.95')


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

from decimal import Decimal

from django.test import TestCase
from django.core.exceptions import ValidationError

from apps.bluebottle_utils.tests import UserTestsMixin
from apps.projects.tests import ProjectTestsMixin

from .models import Donation, DonationLine


class DonationTests(TestCase, ProjectTestsMixin, UserTestsMixin):
    """ Tests for donations. """

    def setUp(self):
        """ Setup a user and a project. """

        self.user = self.create_user()

        self.project = self.create_project()
        self.project.save()

    def test_donationsave(self):
        """ Test if saving a donation works. """

        donation = Donation(user=self.user)
        donation.amount = Decimal('20.00')
        donation.save()

    def test_donationlinesave(self):
        """ Test if saving a donation line works. """

        donation = Donation(user=self.user)
        donation.amount = Decimal('20.00')
        donation.save()

        donationline = DonationLine(donation=donation, project=self.project)
        donationline.amount = Decimal('5.00')
        donationline.save()

    def test_unicode(self):
        """ Test to see wheter unicode representations will fail or not. """
        donation = Donation(user=self.user)
        self.assertTrue(unicode(donation))

        donationline = DonationLine(donation=donation, project=self.project)
        self.assertTrue(unicode(donationline))

    def test_donationvalidation(self):
        """ Test validation for DonationLine objects. """

        donation = Donation(user=self.user)
        donation.amount = Decimal('20.00')
        donation.save()

        # 21 should raise an error because it's more than 20
        donationline = DonationLine(donation=donation, project=self.project)
        donationline.amount = Decimal('21.00')
        self.assertRaises(ValidationError, donationline.full_clean)

        # 19 should be fine
        donationline = DonationLine(donation=donation, project=self.project)
        donationline.amount = Decimal('19.00')
        donationline.full_clean()

        # 20 should be fine
        donationline = DonationLine(donation=donation, project=self.project)
        donationline.amount = Decimal('20.00')
        donationline.full_clean()

        # Now check wheter it is actually updated
        # Add a donation of 5 and see whether 16 raises an error and
        # 15 does not
        donationline = DonationLine(donation=donation, project=self.project)
        donationline.amount = Decimal('5.00')
        donationline.save()

        # 16 should now raise an error
        donationline = DonationLine(donation=donation, project=self.project)
        donationline.amount = Decimal('16.00')
        self.assertRaises(ValidationError, donationline.full_clean)

        # 15 should be fine
        donationline = DonationLine(donation=donation, project=self.project)
        donationline.amount = Decimal('15.00')
        donationline.full_clean()

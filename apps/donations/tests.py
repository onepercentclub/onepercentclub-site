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

    def test_donationupdate(self):
        """ Regression test for updating donationlines. """

        donation = Donation(user=self.user)
        donation.amount = Decimal('20.00')
        donation.save()

        # 21 should raise an error because it's more than 20
        donationline = DonationLine(donation=donation, project=self.project)
        donationline.amount = Decimal('20.00')
        donationline.save()

        # Updating to 19 should be fine
        donationline.amount = Decimal('19.00')
        donationline.full_clean()

    def test_supporters(self):
        """
        Test whether project supporters are properly returned.

        TODO: This *might* belong in the projects app *but* this would
        yield a cyclical import. Solution: turn tests into module with
        base classes in `base.py` instead of having everything in one file.
        """

        donation = Donation(user=self.user)
        donation.amount = Decimal('20.00')
        donation.save()

        donationline = DonationLine(donation=donation, project=self.project)
        donationline.amount = Decimal('5.00')
        donationline.save()

        # Test wether a single supporter is properly listed
        supporters = list(self.project.get_supporters())

        self.assertEqual(supporters, [self.user])

        # Add another
        other_user = self.create_user()

        donation = Donation(user=other_user)
        donation.amount = Decimal('20.00')
        donation.save()

        donationline = DonationLine(donation=donation, project=self.project)
        donationline.amount = Decimal('5.00')
        donationline.save()

        supporters = self.project.get_supporters()
        self.assertTrue(other_user in supporters)
        self.assertEquals(supporters.count(), 2)

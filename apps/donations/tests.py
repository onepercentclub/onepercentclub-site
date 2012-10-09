from decimal import Decimal

from django.test import TestCase
from django.core.exceptions import ValidationError

from apps.bluebottle_utils.tests import UserTestsMixin
from apps.projects.tests import ProjectTestsMixin

from .models import Donation


class DonationTestsMixin(ProjectTestsMixin, UserTestsMixin):
    """ Base class for tests using donations. """

    def create_donation(self, user=None, amount=None, project=None, status='closed'):
        if not project:
            project = self.create_project()
            project.save()

        if not user:
            user = self.create_user()

        if not amount:
            amount = Decimal('10.00')

        return Donation(user=user, amount=amount, status=status, project=project)

class DonationTests(TestCase, DonationTestsMixin, ProjectTestsMixin):
    """ Tests for donations. """

    def test_donationsave(self):
        """ Test if saving a donation works. """

        donation = self.create_donation()
        donation.save()

    def test_unicode(self):
        """ Test to see wheter unicode representations will fail or not. """
        project = self.create_project(title="Prima project")
        project.save()
        donation = self.create_donation(amount = 35, project=project)
        donation.save()
        
        donation_str = unicode(donation)
        self.assertTrue(donation_str)
        self.assertIn('35', donation_str)
        self.assertIn('Prima project', donation_str)

    def test_donationvalidation(self):
        """ Test validation for DonationLine objects. """

        donation = self.create_donation(amount=Decimal('20.00'))
        donation.save()


    def test_supporters(self):
        """
        Test whether project supporters are properly returned.

        TODO: This *might* belong in the projects app *but* this would
        yield a cyclical import. Solution: turn tests into module with
        base classes in `base.py` instead of having everything in one file.
        """
        project = self.create_project(
            title='Banana Project',
            slug='banana'
        )
        project.save()

        other_user = self.create_user()
        donation = self.create_donation(project=project, user=other_user)
        donation.save()

        # Test wether a single supporter is properly listed
        supporters = list(project.get_supporters())

        self.assertEqual(supporters, [donation.user])

        # Add another
        other_user = self.create_user()
        donation = self.create_donation(project=project, user=other_user)
        donation.save()


        supporters = project.get_supporters()
        self.assertIn(other_user, supporters)
        self.assertEquals(supporters.count(), 2)

        # second payment by the other_user
        donation = self.create_donation(project=project, user=other_user)
        donation.save()

        # other_user should only be listed once
        supporters = project.get_supporters()
        self.assertEquals(supporters.count(), 2)
        
        # Add a poor guy 
        poor_guy = self.create_user()
        donation = self.create_donation(
                            project=project, 
                            user=poor_guy,
                            status='cancelled')
        donation.save()

        # Since donation was cancelled it still should be 2 supporters 
        supporters = project.get_supporters()
        self.assertEquals(supporters.count(), 2)
        


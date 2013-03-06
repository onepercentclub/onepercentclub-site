from decimal import Decimal
from django.test import TestCase
from apps.bluebottle_utils.tests import UserTestsMixin
from apps.projects.tests import ProjectTestsMixin
from rest_framework import status
from .models import Donation


class DonationTestsMixin(ProjectTestsMixin, UserTestsMixin):
    """ Base class for tests using donations. """

    def create_donation(self, user=None, amount=None, project=None, status='new'):
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
        """ Test to see whether unicode representations will fail or not. """
        project = self.create_project(title="Prima project")
        project.save()
        donation = self.create_donation(amount=3500, project=project)
        donation.save()

        donation_str = unicode(donation)
        self.assertTrue(donation_str)
        self.assertIn('35', donation_str)
        self.assertIn('Prima project', donation_str)

    def test_donationvalidation(self):
        """ Test validation for DonationLine objects. """

        donation = self.create_donation(amount=Decimal('20.00'))
        donation.save()


# Integration tests for API

class CartApiIntegrationTest(ProjectTestsMixin, TestCase):
    """
    Integration tests for the adding Donations to an Order (a cart in this case)
    """

    def setUp(self):
        self.some_project = self.create_project()
        self.another_project = self.create_project()
        self.some_user = self.create_user()
        self.another_user = self.create_user()
        self.current_donations_url = '/i18n/api/fund/orders/current/donations/'
        self.current_order_url = '/i18n/api/fund/orders/current'

    def test_current_order_donation_crud(self):
        """
        Tests for creating, retrieving, updating and deleting a donation to shopping cart.
        """

        # First make sure we have a current order
        self.client.login(username=self.some_user.username, password='password')
        response = self.client.get(self.current_order_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['status'], 'current')

        # Create a Donation
        response = self.client.post(self.current_donations_url, {'project': self.some_project.slug, 'amount': 35})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['amount'], '35.00')
        self.assertEqual(response.data['project'], self.some_project.slug)
        self.assertEqual(response.data['status'], 'new')

        # Retrieve the created Donation
        donation_detail_url = "{0}{1}".format(self.current_donations_url, response.data['id'])
        response = self.client.get(donation_detail_url)
        self.assertEqual(response.data['amount'], '35.00')
        self.assertEqual(response.data['project'], self.some_project.slug)

        # Retrieve the list with all donations in this cart should return one
        response = self.client.get(self.current_donations_url)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['amount'], '35.00')
        self.assertEqual(response.data['results'][0]['project'], self.some_project.slug)

        # Create another Donation
        response = self.client.post(self.current_donations_url,
                                    {'project': self.another_project.slug, 'amount': '12.50'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['amount'], '12.50')
        self.assertEqual(response.data['project'], self.another_project.slug)

        # Retrieve the list with all donations in this cart should return one
        response = self.client.get(self.current_donations_url)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['amount'], '35.00')
        self.assertEqual(response.data['results'][1]['amount'], '12.50')
        self.assertEqual(response.data['results'][0]['project'], self.some_project.slug)

        # Update the created Donation by owner.
        response = self.client.put(donation_detail_url, {'amount': 150, 'project': self.some_project.slug})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['amount'], '150.00')

        # Update the status of the created Donation by owner should be ignored
        response = self.client.put(donation_detail_url,
                                   {'amount': 150, 'project': self.some_project.slug, 'status': 'paid'})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['amount'], '150.00')
        self.assertEqual(response.data['status'], 'new')

        # Delete a donation should work the list should have one donation now
        response = self.client.delete(donation_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)
        response = self.client.get(self.current_donations_url)
        self.assertEqual(response.data['count'], 1)

        # Another user should not see the cart of the first user
        self.client.logout()
        self.client.login(username=self.another_user.username, password='password')
        # make a cart for this another user
        self.client.get(self.current_order_url)
        response = self.client.get(self.current_donations_url)
        self.assertEqual(response.data['count'], 0)

        # Another user should not be able to view a donation in the cart of the first user
        response = self.client.get(donation_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

        # Now let's get anonymous and create a donation
        self.client.logout()
        # make a cart for this anonymous user
        self.client.get(self.current_order_url)
        response = self.client.post(self.current_donations_url, {'project': self.some_project.slug, 'amount': 71})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['amount'], '71.00')
        self.assertEqual(response.data['project'], self.some_project.slug)
        self.assertEqual(response.data['status'], 'new')
        response = self.client.get(self.current_donations_url)
        self.assertEqual(response.data['count'], 1)

        # Login and out again... The anonymous cart should NOT be returned
        self.client.login(username=self.some_user.username, password='password')
        self.client.logout()
        self.client.get(self.current_order_url)
        response = self.client.get(self.current_donations_url)
        self.assertEqual(response.data['count'], 0)

        # Login as the first user and cart should still have one donation
        self.client.login(username=self.some_user.username, password='password')
        response = self.client.get(self.current_donations_url)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['amount'], '12.50')
        self.assertEqual(response.data['results'][0]['project'], self.another_project.slug)
        self.client.logout()

    def test_current_order_monthly(self):
        # Test setting a recurring order as logged in user.
        self.client.login(username=self.some_user.username, password='password')
        response = self.client.get(self.current_order_url)
        self.assertEqual(response.data['recurring'], False)
        response = self.client.put(self.current_order_url, {'recurring': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['recurring'], True)

        # Test that setting a recurring order as anonymous user fails.
        self.client.logout()
        response = self.client.get(self.current_order_url)
        self.assertEqual(response.data['recurring'], False)
        response = self.client.put(self.current_order_url, {'recurring': True})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(self.current_order_url)
        self.assertEqual(response.data['recurring'], False)


class VoucherApiIntegrationTest(ProjectTestsMixin, TestCase):
    """
    Integration tests for the adding Donations to an Order (a cart in this case)
    """

    def setUp(self):
        self.some_project = self.create_project()
        self.another_project = self.create_project()
        self.some_user = self.create_user()
        self.another_user = self.create_user()
        self.current_vouchers_url = '/i18n/api/fund/orders/current/vouchers/'
        self.vouchers_url = '/i18n/api/fund/vouchers/'
        self.current_order_url = '/i18n/api/fund/orders/current'
        self.some_voucher_data = {
            'amount': 25, 'text': 'Look at this!',
            'receiver_name': 'Bart', 'receiver_email': 'bart@1procentclub.nl',
            'sender_name': 'Webmaster', 'sender_email': 'webmaster@1procentclub.nl'
        }
        self.another_voucher_data = {
            'amount': 50, 'receiver_email': 'you@1procentclub.nl', 'sender_email': 'me@1procentclub.nl'
        }

    def test_current_order_voucher_crud(self):
        """
        Tests for creating, retrieving, updating and deleting a voucher to shopping cart.
        """

        # First make sure we have a current order
        self.client.login(username=self.some_user.username, password='password')
        response = self.client.get(self.current_order_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['status'], 'current')

        # Create a Voucher.
        response = self.client.post(self.current_vouchers_url, self.some_voucher_data)
        some_voucher_detail_url = '{0}{1}'.format(self.current_vouchers_url, response.data['id'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['amount'], '25.00')
        self.assertEqual(response.data['receiver_name'], self.some_voucher_data['receiver_name'])
        self.assertEqual(response.data['status'], 'new')

        # Create another voucher.
        response = self.client.post(self.current_vouchers_url, self.another_voucher_data)
        another_voucher_detail_url = '{0}{1}'.format(self.current_vouchers_url, response.data['id'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['amount'], '50.00')
        self.assertEqual(response.data['receiver_email'], self.another_voucher_data['receiver_email'])
        self.assertEqual(response.data['status'], 'new')

        # Check that the order now holds that two vouchers.
        response = self.client.get(self.current_order_url)
        self.assertEqual(response.data['amount'], '75.00')
        response = self.client.get(self.current_vouchers_url)
        self.assertEqual(len(response.data['results']), 2)

        # Remove the first voucher and see if all is updated correctly.
        response = self.client.delete(some_voucher_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(self.current_order_url)
        self.assertEqual(response.data['amount'], '50.00')
        response = self.client.get(self.current_vouchers_url)
        self.assertEqual(len(response.data['results']), 1)

        # Setting 77 as amount should fail
        self.some_voucher_data['amount'] = 77
        response = self.client.post(self.current_vouchers_url, self.some_voucher_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

        # Sending a status should not be saved
        self.some_voucher_data['amount'] = 10
        self.some_voucher_data['status'] = 'paid'
        response = self.client.post(self.current_vouchers_url, self.some_voucher_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['amount'], '10.00')
        self.assertEqual(response.data['receiver_email'], self.some_voucher_data['receiver_email'])
        self.assertEqual(response.data['status'], 'new')

        # Updating the amount on a voucher is fine
        self.another_voucher_data['amount'] = 100
        response = self.client.put(another_voucher_detail_url, self.another_voucher_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['amount'], '100.00')

        self.some_voucher_data['receiver_email'] = 'not good'
        self.some_voucher_data['sender_email'] = None
        response = self.client.post(self.current_vouchers_url, self.some_voucher_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)





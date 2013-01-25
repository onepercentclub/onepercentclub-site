from decimal import Decimal
from django.test import TestCase
from apps.bluebottle_utils.tests import UserTestsMixin
from apps.projects.tests import ProjectTestsMixin
from rest_framework import status
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
        self.cart_donations_url = '/i18n/api/fund/cart/donations/'

    def test_cart_donation_crud(self):
        """
        Tests for creating, retrieving, updating and deleting a donation to shopping cart.
        """

        # Create a Donation
        self.client.login(username=self.some_user.username, password='password')
        response = self.client.post(self.cart_donations_url, {'project': self.some_project.id, 'amount': 35})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['amount'], 35)
        self.assertEqual(response.data['project'], self.some_project.id)
        self.assertEqual(response.data['status'], 'cart')

        # Retrieve the created Donation
        donation_detail_url = "{0}{1}".format(self.cart_donations_url, response.data['id'])
        response = self.client.get(donation_detail_url)
        self.assertEqual(response.data['amount'], 35)
        self.assertEqual(response.data['project'], self.some_project.id)

        # Retrieve the list with all donations in this cart should return one
        response = self.client.get(self.cart_donations_url)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['amount'], 35)
        self.assertEqual(response.data['results'][0]['project'], self.some_project.id)

        # Create another Donation
        response = self.client.post(self.cart_donations_url, {'project': self.another_project.id, 'amount': 12.50})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['amount'], Decimal('12.5'))
        self.assertEqual(response.data['project'], self.another_project.id)

        # Retrieve the list with all donations in this cart should return one
        response = self.client.get(self.cart_donations_url)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['amount'], 35)
        self.assertEqual(response.data['results'][1]['amount'], Decimal('12.5'))
        self.assertEqual(response.data['results'][0]['project'], self.some_project.id)

        # Update the created Donation by owner.
        response = self.client.put(donation_detail_url, {'amount': 150, 'project': self.some_project.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['amount'], 150)

        # Update the status of the created Donation by owner should be ignored
        response = self.client.put(donation_detail_url, {'amount': 150, 'project': self.some_project.id, 'status': 'paid'})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['amount'], 150)
        self.assertEqual(response.data['status'], 'cart')

        # Delete a donation should work the list should have one donation now
        response = self.client.delete(donation_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)
        response = self.client.get(self.cart_donations_url)
        self.assertEqual(response.data['count'], 1)

        # Another user should not see the cart of the first user
        self.client.logout()
        self.client.login(username=self.another_user.username, password='password')
        response = self.client.get(self.cart_donations_url)
        self.assertEqual(response.data['count'], 0)

        # Another user should not be able to view a donation in the cart of the first user
        response = self.client.get(donation_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

        # Now let's get anonymous and create a donation
        self.client.logout()
        response = self.client.post(self.cart_donations_url, {'project': self.some_project.id, 'amount': 71})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['amount'], 71)
        self.assertEqual(response.data['project'], self.some_project.id)
        self.assertEqual(response.data['status'], 'cart')
        response = self.client.get(self.cart_donations_url)
        self.assertEqual(response.data['count'], 1)

        # Login and out again... The anonymous cart should NOT be returned
        self.client.login(username=self.some_user.username, password='password')
        self.client.logout()
        response = self.client.get(self.cart_donations_url)
        self.assertEqual(response.data['count'], 0)

        # Login as the first user and cart should still have one donation
        self.client.login(username=self.some_user.username, password='password')
        response = self.client.get(self.cart_donations_url)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['amount'],Decimal('12.5'))
        self.assertEqual(response.data['results'][0]['project'], self.another_project.id)



class SelectPaymentMethodIntegrationTest(ProjectTestsMixin, TestCase):
    """
    Integration tests for the adding Donations to an Order (a cart in this case)
    """

    def setUp(self):
        self.some_project = self.create_project()
        self.another_project = self.create_project()
        self.some_user = self.create_user()
        self.another_user = self.create_user()
        self.cart_donations_url = '/i18n/api/fund/cart/donations/'
        self.checkout_url = '/i18n/api/fund/checkout'
        self.payment_methods_url = '/i18n/api/fund/paymentmethods/'


    def test_show_payment_methods(self):
        """
        Tests for showing payment methods
        """

        # View a list of payment methods. There should be some due to fixtures
        response = self.client.get(self.payment_methods_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        method_detail_url = "{0}{1}".format(self.payment_methods_url, response.data['results'][0]['id'])
        method_detail_slug = response.data['results'][0]['slug']

        # Get paymentmethod detail for the first method should return the right one (same slug)
        response = self.client.get(method_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['slug'], method_detail_slug)

    def test_select_payment_method(self):
        """
        Tests for selecting a payment method. This will create a Payment object too.
        """

        # Create two donations
        self.client.login(username=self.some_user.username, password='password')
        self.client.post(self.cart_donations_url, {'project': self.some_project.id, 'amount': 35})
        self.client.post(self.cart_donations_url, {'project': self.another_project.id, 'amount': 27.50})
        response = self.client.get(self.cart_donations_url)
        self.assertEqual(response.data['count'], 2)

        # Check that payment adds up to the right amount
        response = self.client.get(self.checkout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], Decimal('62.5'))

        # get a paymentmethod and set that for this payment
        response = self.client.get(self.payment_methods_url)
        paymentmethod_id = response.data['results'][0]['id']
        response = self.client.put(self.checkout_url, {'payment_method': paymentmethod_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['payment_method'], paymentmethod_id)







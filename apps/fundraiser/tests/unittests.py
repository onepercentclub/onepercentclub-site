from django.test import TestCase

from rest_framework import status

from bluebottle.bluebottle_utils.tests import UserTestsMixin, generate_random_slug

from apps.fund.models import DonationStatuses, Donation, Order
from apps.projects.models import Project, ProjectPlan, ProjectPhases
from apps.projects.tests.unittests import ProjectTestsMixin

from ..models import FundRaiser


class FundRaiserTestsMixin(object):
    def create_fundraiser(self, owner, project, title=None, amount=5000):
        if not title:
            title = generate_random_slug()

        fr = FundRaiser.objects.create(owner=owner, project=project, title=title, amount=amount)
        return fr

class FundRaiserApiIntegrationTest(FundRaiserTestsMixin, ProjectTestsMixin, UserTestsMixin, TestCase):
    """
    Integration tests for the fundraiser API.
    """

    def setUp(self):
        """ Create two project instances """
        self.some_project = self.create_project(money_asked=50000)
        self.another_project = self.create_project(money_asked=75000)

        self.some_user = self.create_user()
        self.another_user = self.create_user()

        self.fundraiser = self.create_fundraiser(self.some_user, self.some_project)
        self.rundraiser2 = self.create_fundraiser(self.another_user, self.another_project)

        self.current_donations_url = '/api/fund/orders/current/donations/'
        self.current_order_url = '/api/fund/orders/current'
        self.fundraisers_url = '/api/fundraiser/fundraisers/'

    def test_project_fundraisers(self):
        """ Test if the correct fundraisers are returned for a project """

        url = self.fundraisers_url + '?project=' + self.some_project.slug
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(1, response.data['count'])

        fr = response.data['results'][0]
        self.assertEqual(self.some_user.id, fr['owner']['id'])
        self.assertEqual(self.fundraiser.title, fr['title'])
        self.assertEqual('50.00', fr['amount'])
        self.assertEqual('0.00', fr['amount_donated'])

    def test_fundraiser_donations(self):
        """ Test that the correct amounts are returned """
        url_fundraisers = self.fundraisers_url + '?project=' + self.some_project.slug

        # First make sure we have a current order
        self.client.login(username=self.some_user.email, password='password')
        response = self.client.get(self.current_order_url)

        # Create a Donation
        response = self.client.post(self.current_donations_url, {
            'project': self.some_project.slug,
            'amount': 5,
            'fundraiser': self.fundraiser.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['amount'], '5.00')
        self.assertEqual(response.data['fundraiser'], self.fundraiser.id)
        self.assertEqual(response.data['status'], 'new')

        # Create a second donation
        self.client.post(self.current_donations_url, {
            'project': self.some_project.slug,
            'amount': 10,
            'fundraiser': self.fundraiser.id
        })

        response = self.client.get(url_fundraisers)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        # donation is not pending or paid yet
        self.assertEqual('0.00', response.data['results'][0]['amount_donated'])

        donation = Donation.objects.get(pk=1)
        donation.status = DonationStatuses.pending
        donation.save()

        # get the updated status, verify amount donated
        response = self.client.get(url_fundraisers)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual('5.00', response.data['results'][0]['amount_donated'])

        donation.status = DonationStatuses.paid
        donation.save()

        # nothing should be changed
        response = self.client.get(url_fundraisers)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual('5.00', response.data['results'][0]['amount_donated'])

        # check that pending and paid are correctly summed
        donation = Donation.objects.get(pk=2)
        donation.status = DonationStatuses.pending
        donation.save()

        response = self.client.get(url_fundraisers)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual('15.00', response.data['results'][0]['amount_donated'])

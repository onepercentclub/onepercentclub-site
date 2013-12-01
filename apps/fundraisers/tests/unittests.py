from django.utils import timezone
from django.test.client import MULTIPART_CONTENT
import os
import json

from django.core.urlresolvers import reverse
from django.test import TestCase

from rest_framework import status

from bluebottle.bluebottle_utils.tests import UserTestsMixin

from apps.donations.tests.helpers import DonationTestsMixin
from apps.fund.models import DonationStatuses, Donation
from apps.projects.tests.unittests import ProjectTestsMixin

from .helpers import FundRaiserTestsMixin


class FundRaiserApiIntegrationTest(FundRaiserTestsMixin, DonationTestsMixin, ProjectTestsMixin, UserTestsMixin, TestCase):
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
        self.fundraiser2 = self.create_fundraiser(self.another_user, self.another_project)

        self.current_donations_url = '/api/fund/orders/current/donations/'
        self.current_order_url = '/api/fund/orders/current'
        self.fundraiser_list_url = '/api/fundraisers/'
        self.fundraiser_url = '/api/fundraisers/{0}'.format(self.fundraiser.pk)
        self.fundraiser2_url = '/api/fundraisers/{0}'.format(self.fundraiser2.pk)

    def test_project_fundraisers(self):
        """ Test if the correct fundraisers are returned for a project """

        url = self.fundraiser_list_url + '?project=' + self.some_project.slug
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
        url_fundraisers = self.fundraiser_list_url + '?project=' + self.some_project.slug

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

    def test_supporters_for_project(self):
        """
        Test the list of supporters of a project when a fundraiser donation was made.
        """
        self.create_donation(user=self.some_user, project=self.some_project, status=DonationStatuses.paid)

        self.create_donation(user=self.some_user, project=self.some_project, status=DonationStatuses.paid,
                fundraiser=self.fundraiser)

        project_supporter_url = '{0}?project={1}'.format(reverse('project-supporter-list'), self.some_project.slug)
        response = self.client.get(project_supporter_url)

        json_data = json.loads(response.content)
        # Expect donation for project and donation for fundraiser to show up.
        self.assertEqual(len(json_data['results']), 2)
        self.assertFalse('amount' in json_data['results'][0])
        self.assertFalse('amount' in json_data['results'][1])

    def test_supporters_for_fundraiser(self):
        """
        Test the list of supporters for a specific fundraiser.
        """
        self.create_donation(user=self.some_user, project=self.some_project, status=DonationStatuses.paid)

        fundraise_donation = self.create_donation(user=self.some_user, project=self.some_project, status=DonationStatuses.paid,
                fundraiser=self.fundraiser)

        project_supporter_url = '{0}?project={1}&fundraiser={2}'.format(
            reverse('project-supporter-list'),
            self.some_project.slug,
            fundraise_donation.fundraiser.pk,
        )
        response = self.client.get(project_supporter_url)

        json_data = json.loads(response.content)
        # Only expect the donation for the fundraiser to show up.
        self.assertEqual(len(json_data['results']), 1)
        self.assertFalse('amount' in json_data['results'][0])

    def test_donations_for_fundraiser_authenticated(self):
        """
        Test the list of donations for a specific fundraiser.
        """
        self.assertTrue(self.client.login(username=self.some_user.email, password='password'))

        self.create_donation(user=self.some_user, project=self.some_project, status=DonationStatuses.paid)

        fundraise_donation = self.create_donation(user=self.some_user, project=self.some_project, status=DonationStatuses.paid,
                fundraiser=self.fundraiser)

        project_donation_url = '{0}?project={1}&fundraiser={2}'.format(
            reverse('project-donation-list'),
            self.some_project.slug,
            fundraise_donation.fundraiser.pk,
        )
        response = self.client.get(project_donation_url)

        json_data = json.loads(response.content)
        # Only expect the donation for the fundraiser to show up.
        self.assertEqual(len(json_data['results']), 1)
        self.assertTrue('amount' in json_data['results'][0])
        self.assertEqual(json_data['results'][0]['amount'], '1.00')

    def test_donations_for_fundraiser_anonymous(self):
        self.assertTrue(self.client.login(username=self.another_user.email, password='password'))

        self.create_donation(user=self.some_user, project=self.some_project, status=DonationStatuses.paid)

        fundraise_donation = self.create_donation(user=self.some_user, project=self.some_project,
                                                  status=DonationStatuses.paid, fundraiser=self.fundraiser)

        project_donation_url = '{0}?project={1}&fundraiser={2}'.format(
            reverse('project-donation-list'),
            self.some_project.slug,
            fundraise_donation.fundraiser.pk,
        )
        response = self.client.get(project_donation_url)

        json_data = json.loads(response.content)
        # Only expect the donation for the fundraiser to show up.
        self.assertEqual(len(json_data['results']), 0)

    def test_donations_for_fundraiser_not_owner(self):
        fundraise_donation = self.create_donation(user=self.some_user, project=self.some_project, status=DonationStatuses.paid,
                fundraiser=self.fundraiser)

        project_donation_url = '{0}?project={1}&fundraiser={2}'.format(
            reverse('project-donation-list'),
            self.some_project.slug,
            fundraise_donation.fundraiser.pk,
        )
        response = self.client.get(project_donation_url)

        json_data = json.loads(response.content)
        self.assertDictEqual(json_data, {u'detail': u'Authentication credentials were not provided.'})


    def _post_fundraiser_data(self, **kwargs):
        """
        Helper function to post some data to the fundraiser list view.
        """
        # Construct default data
        now = timezone.now()
        data = {
            'project': self.some_project.slug,
            'title': 'My Title',
            'description': 'My Description',
            'amount': '1000',
            'deadline': now.strftime('%Y-%m-%dT%H:%M:%S'),
        }

        # Adjust default data with given kwargs.
        data.update(kwargs)

        # Special case: Image file
        f = None
        if 'image' not in data:
            f = open(os.path.join(os.path.dirname(__file__), 'test_files', 'upload.png'), 'rb')
            data['image'] = f

        response = self.client.post(self.fundraiser_list_url, data)

        if f and not f.closed:
            f.close()

        return response

    def test_create_fundraiser_anonymous(self):
        """
        Test create fundraiser, via fundraiser list API, as anonymous user.
        """
        response = self.client.post(self.fundraiser_list_url, {})
        self.assertEqual(response.status_code, 403)

    def test_create_fundraiser_authenticated(self):
        """
        Test create fundraiser, via fundraiser list API, as authenticated user.
        """
        self.assertTrue(self.client.login(username=self.some_user.email, password='password'))

        # Construct data
        deadline = (timezone.now() + timezone.timedelta(days=14)).strftime('%Y-%m-%dT%H:%M:%S')
        with open(os.path.join(os.path.dirname(__file__), 'test_files', 'upload.png'), 'rb') as fp:
            data = {
                'project': self.some_project.slug,
                'title': 'My Title',
                'description': 'My Description',
                'image': fp,
                'amount': '1000',
                'deadline': deadline,
            }

            # Perform call
            response = self.client.post(self.fundraiser_list_url, data)

        # Validate response
        self.assertEqual(response.status_code, 201)

        json_data = json.loads(response.content)

        self.assertEqual(json_data['title'], 'My Title')
        self.assertEqual(json_data['deadline'], deadline)
        self.assertEqual(json_data['owner']['username'], self.some_user.username)
        self.assertEqual(json_data['project'], self.some_project.slug)

    def test_read_fundraiser_list_anonymous(self):
        """
        Test read fundraiser, via fundraiser list API, as anonymous user.
        """
        response = self.client.get('{0}?project={1}'.format(self.fundraiser_list_url, self.some_project.slug))

        # Validate response
        self.assertEqual(response.status_code, 200)

        json_data = json.loads(response.content)

        self.assertEqual(json_data['count'], 1)
        self.assertEqual(len(json_data['results']), 1)

        json_data = json_data['results'][0]

        self.assertEqual(json_data['title'], self.fundraiser.title)
        # TODO: Timezone difference issue
        #self.assertEqual(json_data['deadline'], self.fundraiser.deadline.strftime('%Y-%m-%dT%H:%M:%S'))
        self.assertEqual(json_data['owner']['username'], self.fundraiser.owner.username)
        self.assertEqual(json_data['project'], self.fundraiser.project.slug)

    def test_read_fundraiser_anonymous(self):
        """
        Test read fundraiser, via fundraiser detail API, as anonymous user.
        """
        response = self.client.get(self.fundraiser_url)

        # Validate response
        self.assertEqual(response.status_code, 200)

        json_data = json.loads(response.content)

        self.assertEqual(json_data['title'], self.fundraiser.title)
        # TODO: Timezone difference issue
        #self.assertTrue(json_data['deadline'].startswith(self.fundraiser.deadline.strftime('%Y-%m-%dT%H:%M:%S')))
        self.assertEqual(json_data['owner']['username'], self.fundraiser.owner.username)
        self.assertEqual(json_data['project'], self.fundraiser.project.slug)

    def test_update_fundraiser_anonymous(self):
        response = self.client.put(self.fundraiser_url, {})
        self.assertEqual(response.status_code, 403)

    def test_update_fundraiser_authenticated_owner(self):
        self.assertEqual(self.some_user, self.fundraiser.owner)

        self.assertTrue(self.client.login(username=self.some_user.email, password='password'))

        # Construct data
        deadline = timezone.now() + timezone.timedelta(days=14)
        with open(os.path.join(os.path.dirname(__file__), 'test_files', 'upload.png'), 'rb') as fp:
            data = {
                'project': self.another_project.slug,
                'title': 'Updated Title',
                'description': 'Updated Description',
                #'image': fp,
                'amount': '2000',
                'deadline': deadline.strftime('%Y-%m-%dT%H:%M:%S'),
            }

            # Perform call
            response = self.client.put(self.fundraiser_url, data, content_type=MULTIPART_CONTENT)

        # Validate response
        # TODO: How can we PUT with a file?
        # self.assertEquals(response.status_code, 200)
        #
        # # Reload fundraiser
        # fundraiser = FundRaiser.objects.get(pk=self.fundraiser.pk)
        #
        # self.assertEqual(data['title'], fundraiser.title)
        # self.assertEquals(deadline, fundraiser.deadline)
        # self.assertEqual(self.some_user, fundraiser.some_user.username)
        # self.assertEqual(data['project'], fundraiser.another_project.slug)

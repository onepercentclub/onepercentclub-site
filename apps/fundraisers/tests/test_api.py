from bluebottle.bb_projects.models import ProjectPhase
from django.utils import timezone
from django.test.client import MULTIPART_CONTENT
from onepercentclub.tests.utils import OnePercentTestCase
import os
import json

from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from django.test import TestCase

from rest_framework import status

from bluebottle.test.factory_models.accounts import BlueBottleUserFactory
from onepercentclub.tests.factory_models.fundraiser_factories import FundRaiserFactory
from onepercentclub.tests.factory_models.project_factories import OnePercentProjectFactory
from onepercentclub.tests.factory_models.donation_factories import DonationFactory

from apps.fund.models import DonationStatuses, Donation


class FundRaiserApiIntegrationTest(OnePercentTestCase):
    """
    Integration tests for the fundraiser API.
    """

    def setUp(self):
        """ Create two project instances """
        self.init_projects()
        self.campaign_phase = ProjectPhase.objects.get(slug='campaign')

        self.some_project = OnePercentProjectFactory.create(amount_asked=50000, status=self.campaign_phase)
        self.another_project = OnePercentProjectFactory.create(amount_asked=75000, status=self.campaign_phase)

        self.some_user = BlueBottleUserFactory.create()
        self.some_user_token = "JWT {0}".format(self.some_user.get_jwt_token())

        self.another_user = BlueBottleUserFactory.create()
        self.another_user_token = "JWT {0}".format(self.another_user.get_jwt_token())

        self.fundraiser = FundRaiserFactory.create(owner=self.some_user, project=self.some_project)
        self.fundraiser2 = FundRaiserFactory.create(owner=self.another_user, project=self.another_project)

        self.current_donations_url = reverse('fund-order-current-donation-list')
        self.current_order_url = reverse('fund-order-current-detail')
        self.fundraiser_list_url = reverse('fundraiser-list')
        self.fundraiser_url = reverse('fundraiser-detail', kwargs={'pk': self.fundraiser.pk})
        self.fundraiser2_url = reverse('fundraiser-detail', kwargs={'pk': self.fundraiser2.pk})

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
        response = self.client.get(self.current_order_url, HTTP_AUTHORIZATION=self.some_user_token)

        # Create a Donation
        response = self.client.post(self.current_donations_url, {
            'project': self.some_project.slug,
            'amount': 5,
            'fundraiser': self.fundraiser.id
        }, HTTP_AUTHORIZATION=self.some_user_token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['amount'], '5.00')
        self.assertEqual(response.data['fundraiser'], self.fundraiser.id)
        self.assertEqual(response.data['status'], 'new')

        # Create a second donation
        self.client.post(self.current_donations_url, {
            'project': self.some_project.slug,
            'amount': 10,
            'fundraiser': self.fundraiser.id
        }, HTTP_AUTHORIZATION=self.some_user_token)

        response = self.client.get(url_fundraisers, HTTP_AUTHORIZATION=self.some_user_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        # donation is not pending or paid yet
        self.assertEqual('0.00', response.data['results'][0]['amount_donated'])

        donation = Donation.objects.order_by('created').all()[0]
        donation.status = DonationStatuses.pending
        donation.save()

        # get the updated status, verify amount donated
        response = self.client.get(url_fundraisers, HTTP_AUTHORIZATION=self.some_user_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual('5.00', response.data['results'][0]['amount_donated'])

        donation.status = DonationStatuses.paid
        donation.save()

        # nothing should be changed
        response = self.client.get(url_fundraisers, HTTP_AUTHORIZATION=self.some_user_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual('5.00', response.data['results'][0]['amount_donated'])

        # check that pending and paid are correctly summed
        donation = Donation.objects.order_by('created').all()[1]
        donation.status = DonationStatuses.pending
        donation.save()

        response = self.client.get(url_fundraisers, HTTP_AUTHORIZATION=self.some_user_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual('15.00', response.data['results'][0]['amount_donated'])

    def test_supporters_for_project(self):
        """
        Test the list of supporters of a project when a fundraiser donation was made.
        """
        DonationFactory.create(user=self.some_user, project=self.some_project, status=DonationStatuses.paid)

        DonationFactory.create(user=self.some_user, project=self.some_project, status=DonationStatuses.paid,
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
        DonationFactory.create(user=self.some_user, project=self.some_project, status=DonationStatuses.paid)

        fundraise_donation = DonationFactory.create(user=self.some_user, project=self.some_project, status=DonationStatuses.paid,
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
        fundraise_donation = DonationFactory.create(user=self.some_user, project=self.some_project, amount=5000,
                                                    status=DonationStatuses.paid, fundraiser=self.fundraiser)

        project_donation_url = '{0}?project={1}&fundraiser={2}'.format(
            reverse('project-donation-list'),
            self.some_project.slug,
            fundraise_donation.fundraiser.pk,
        )

        response = self.client.get(project_donation_url, HTTP_AUTHORIZATION=self.some_user_token)
        json_data = json.loads(response.content)

        self.assertEqual(len(json_data['results']), 1)
        self.assertTrue('amount' in json_data['results'][0])
        self.assertEqual(json_data['results'][0]['amount'], '50.00')

    def test_donations_for_fundraiser_anonymous(self):
        DonationFactory.create(user=self.some_user, project=self.some_project, status=DonationStatuses.paid)

        fundraise_donation = DonationFactory.create(user=self.some_user, project=self.some_project,
                                                  status=DonationStatuses.paid, fundraiser=self.fundraiser)

        project_donation_url = '{0}?project={1}&fundraiser={2}'.format(
            reverse('project-donation-list'),
            self.some_project.slug,
            fundraise_donation.fundraiser.pk,
        )
        response = self.client.get(project_donation_url, HTTP_AUTHORIZATION=self.another_user_token)

        json_data = json.loads(response.content)

        # Only expect the donation for the fundraiser to show up.
        self.assertEqual(len(json_data['results']), 0)

    def test_donations_for_fundraiser_not_owner(self):
        fundraise_donation = DonationFactory.create(user=self.some_user, project=self.some_project, status=DonationStatuses.paid,
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
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_fundraiser_authenticated(self):
        """
        Test create fundraiser, via fundraiser list API, as authenticated user.
        """
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
            response = self.client.post(self.fundraiser_list_url, data, HTTP_AUTHORIZATION=self.some_user_token)

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
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_fundraiser_authenticated_owner(self):
        self.assertEqual(self.some_user, self.fundraiser.owner)

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
            response = self.client.put(self.fundraiser_url, data, content_type=MULTIPART_CONTENT,
                                        HTTP_AUTHORIZATION=self.some_user_token)

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

from mock import patch

from django.core.urlresolvers import reverse

from rest_framework.authtoken.models import Token
from rest_framework import status

from bluebottle.bb_donations.tests.test_api import DonationApiTestCase
from bluebottle.bb_orders.views import ManageOrderDetail

from bluebottle.test.factory_models.projects import ProjectFactory
from bluebottle.test.factory_models.orders import OrderFactory
from bluebottle.test.factory_models.donations import DonationFactory
from bluebottle.test.factory_models.fundraisers import FundRaiserFactory


@patch.object(ManageOrderDetail, 'check_status_psp')
class TestDonationList(DonationApiTestCase):
    """
    Test that the fundraiser donations list only works for the fundraiser owner
    """
    def setUp(self):
        super(TestDonationList, self).setUp()

        # Make user 1 a staff user
        self.user1.is_staff = True
        self.user1.save()

        # Create a target project/fundraiser
        self.project = ProjectFactory.create(amount_asked=5000, owner=self.user1)
        self.project.set_status('campaign')

        self.fundraiser = FundRaiserFactory.create(amount=4000, owner=self.user1, 
            project=self.project)

        # Two users make a donations
        order1 = OrderFactory.create(user=self.user1)
        self.donation1 = DonationFactory.create(amount=1000, project=self.project, 
            fundraiser=self.fundraiser, order=order1)
        order1.locked()
        order1.succeeded()

        # Create the second without fundraiser
        order2 = OrderFactory.create(user=self.user2)
        self.donation2 = DonationFactory.create(amount=1000, 
            project=self.project, fundraiser=None, order=order2)
        order2.locked()
        order2.succeeded()

        self.fundraiser_donation_list_url = reverse('fund-ticker-list')

    def test_latest_donation_list(self, check_status_psp):
        user_token = Token.objects.create(user=self.user1)
        response = self.client.get(self.fundraiser_donation_list_url, 
            HTTP_AUTHORIZATION="Token {0}".format(user_token))

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data['results']), 2)

        # Second donation (first in list) without fundraiser
        donation2_data = response.data['results'][0]
        self.assertEqual(donation2_data['id'], self.donation2.id)
        self.assertEqual(donation2_data['project']['title'], self.project.title)
        self.assertTrue(donation2_data['project']['country']['name'])
        self.assertEqual(donation2_data['user']['full_name'], self.user2.full_name)
        
        # First donation without fundraiser
        donation1_data = response.data['results'][1]
        self.assertEqual(donation1_data['fundraiser'], self.fundraiser.id)


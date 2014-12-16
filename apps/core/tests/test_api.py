from decimal import Decimal
from mock import patch
from bunch import bunchify

from django.core.urlresolvers import reverse

from rest_framework.authtoken.models import Token
from rest_framework import status

from bluebottle.bb_donations.tests.test_api import DonationApiTestCase
from bluebottle.bb_orders.views import ManageOrderDetail

from bluebottle.test.factory_models.projects import ProjectFactory
from bluebottle.test.factory_models.orders import OrderFactory
from bluebottle.test.factory_models.donations import DonationFactory
from bluebottle.test.factory_models.fundraisers import FundraiserFactory


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

        self.fundraiser = FundraiserFactory.create(amount=4000, owner=self.user1,
            project=self.project)

        # Two users make a donations
        order1 = OrderFactory.create(user=self.user1)
        self.donation1 = DonationFactory.create(amount=15, project=self.project, 
            fundraiser=self.fundraiser, order=order1)
        order1.locked()
        order1.succeeded()

        # Create the second without fundraiser
        order2 = OrderFactory.create(user=self.user2)
        self.donation2 = DonationFactory.create(amount=10, 
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
        data1 = bunchify(response.data['results'][0])

        self.assertEqual(data1.id, self.donation2.id)
        self.assertEqual(data1.amount, Decimal('10'))
        self.assertEqual(data1.project.title, self.project.title)
        self.assertTrue(data1.project.country.name)
        self.assertEqual(data1.user.full_name, self.user2.get_full_name())
        self.assertEqual(data1.project.image, '')
        self.assertEqual(data1.project.owner.avatar, '')
        
        # First donation without fundraiser
        data2 = bunchify(response.data['results'][1])

        self.assertEqual(data2['amount'], Decimal('15'))
        self.assertEqual(data2['fundraiser'], self.fundraiser.id)


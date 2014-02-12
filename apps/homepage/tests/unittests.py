from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify

from rest_framework import status

from apps.campaigns.models import Campaign
from apps.fund.models import Donation, DonationStatuses, Order
from apps.fundraisers.tests.helpers import FundRaiserTestsMixin

from apps.projects.tests.unittests import ProjectTestsMixin


class HomepageTestCase(FundRaiserTestsMixin, ProjectTestsMixin, TestCase):
    """ Test that the homepage doesn't error out if no/a campaign is available """

    def setUp(self):
        User = get_user_model()
        # Create and activate user.
        self.user = User.objects.create_user('johndoe@example.com', 'secret', primary_language='en')
        title = u'Mobile payments for everyone 2!'

        self.project = self.create_project(title=title, slug=slugify(title), money_asked=100000, owner=self.user)
        self.project.is_campaign = True
        self.project.projectcampaign.money_donated = 0
        self.project.projectcampaign.save()
        self.project.save()

        self.homepage_url = '/api/homepage/en'

    def test_homepage_without_campaign(self):
        response = self.client.get(self.homepage_url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        self.assertEqual(None, response.data['campaign'])

        project = response.data['projects'][0]
        self.assertTrue(project['is_campaign'])


    def test_homepage_with_campaign(self):
        now = timezone.now()
        start, end = now - timedelta(hours=8), now + timedelta(weeks=1)
        Campaign.objects.create(start=start, end=end, title='FooBarCaMpAIgN', target=100000)

        # make a donation before the campaign starts
        order = Order.objects.create(user=self.user, order_number=1)
        Donation.objects.create(amount=1000, user=self.user, project=self.project,
                                status=DonationStatuses.paid, order=order, ready=now-timedelta(days=1))

        # and a couple of donations in campaign, for a total amount of 2000+3000+4000 cents = 90 euros
        for i in range(1,4):
            amount = (i+1)*1000
            Donation.objects.create(amount=amount, user=self.user, project=self.project,
                                    status=DonationStatuses.paid, order=order, ready=now+timedelta(days=i))

        # and one after the campaign
        Donation.objects.create(amount=5000, user=self.user, project=self.project,
                                status=DonationStatuses.paid, order=order, ready=now+timedelta(weeks=2))

        self.project_with_fundraiser = self.create_project(money_asked=50000)
        self.project_with_fundraiser.is_campaign = True
        self.project_with_fundraiser.save()
        self.fundraiser = self.create_fundraiser(self.user, self.project_with_fundraiser)

        response = self.client.get(self.homepage_url)
        self.assertNotEqual(None, response.data['campaign'])

        self.assertEqual(response.data['campaign']['amount_donated'], '90.00')

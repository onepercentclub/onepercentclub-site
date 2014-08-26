from datetime import timedelta
from bluebottle.bb_projects.models import ProjectPhase
from bluebottle.test.factory_models.accounts import BlueBottleUserFactory
from bluebottle.test.factory_models.utils import LanguageFactory
from bluebottle.utils.model_dispatcher import get_donation_model, get_order_model

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify
from onepercentclub.tests.factory_models.fundraiser_factories import FundRaiserFactory
from onepercentclub.tests.factory_models.project_factories import OnePercentProjectFactory
from onepercentclub.tests.utils import OnePercentTestCase

from rest_framework import status

from apps.campaigns.models import Campaign

DONATION_MODEL = get_donation_model()
ORDER_MODEL = get_order_model()

class HomepageTestCase(OnePercentTestCase):
    """ Test that the homepage doesn't error out if no/a campaign is available """

    def setUp(self):
        self.init_projects()

        # Create and activate user.
        self.user = BlueBottleUserFactory.create(email='johndoe@example.com', primary_language='en')
        title = u'Mobile payments for everyone 2!'
        language = LanguageFactory.create(code='en')

        self.project = OnePercentProjectFactory.create(title=title, slug=slugify(title), amount_asked=100000, owner=self.user)
        self.project.status = ProjectPhase.objects.get(slug='campaign')
        self.project.is_campaign = True
        self.project.money_donated = 0
        self.project.language = language
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
        order = ORDER_MODEL.objects.create(user=self.user, order_number=1)
        DONATION_MODEL.objects.create(amount=1000, user=self.user, project=self.project,
                                status=DONATION_MODEL.DonationStatuses.paid, order=order, ready=now-timedelta(days=1))

        # and a couple of donations in campaign, for a total amount of 2000+3000+4000 cents = 90 euros
        for i in range(1,4):
            amount = (i+1)*1000
            DONATION_MODEL.objects.create(amount=amount, user=self.user, project=self.project,
                                    status=DONATION_MODEL.DonationStatuses.paid, order=order, ready=now+timedelta(days=i))

        # and one after the campaign
        DONATION_MODEL.objects.create(amount=5000, user=self.user, project=self.project,
                                status=DONATION_MODEL.DonationStatuses.paid, order=order, ready=now+timedelta(weeks=2))

        self.project_with_fundraiser = OnePercentProjectFactory.create(amount_asked=50000)
        self.project_with_fundraiser.is_campaign = True
        self.project_with_fundraiser.save()
        self.fundraiser = FundRaiserFactory.create(owner=self.user, project=self.project_with_fundraiser)

        response = self.client.get(self.homepage_url)
        self.assertNotEqual(None, response.data['campaign'])

        self.assertEqual(response.data['campaign']['amount_donated'], '90.00')

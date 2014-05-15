from datetime import timedelta
from bluebottle.test.factory_models.accounts import BlueBottleUserFactory

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings
from django.utils.unittest.case import skipUnless
from onepercentclub.tests.factory_models.fundraiser_factories import FundRaiserFactory
from onepercentclub.tests.factory_models.project_factories import OnePercentProjectFactory

from onepercentclub.tests.utils import OnePercentSeleniumTestCase

from apps.campaigns.models import Campaign

@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
        'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class HomepageTestCase(OnePercentSeleniumTestCase):
    """ Test that the homepage doesn't error out if no/a campaign is available """

    def setUp(self):
        self.init_projects()

        self.projects = dict([(slugify(title), title) for title in [
           u'Mobile payments for everyone 2!', u'Schools for children 2',  u'Women first 2'
        ]])

        User = get_user_model()
        # Create and activate user.
        self.user = BlueBottleUserFactory.create(email='johndoe@example.com', primary_language='en')

        for slug, title in self.projects.items():
            project = OnePercentProjectFactory.create(title=title, slug=slug, amount_asked=100000, owner=self.user)
            project.amount_donated = 0
            project.save()

    def test_homepage_without_campaign(self):
        self.visit_homepage()

        self.assertTrue(self.browser.is_text_present('CHOOSE YOUR PROJECT'))

    def test_homepage_with_campaign(self):
        start, end = timezone.now() - timedelta(hours=8), timezone.now() + timedelta(weeks=1)
        Campaign.objects.create(start=start, end=end, title='FooBarCaMpAIgN', target=100000)

        self.project_with_fundraiser = OnePercentProjectFactory.create(amount_asked=50000)
        self.project_with_fundraiser.is_campaign = True
        self.project_with_fundraiser.save()
        self.fundraiser = FundRaiserFactory.create(owner=self.user, project=self.project_with_fundraiser)

        self.visit_homepage()
        self.assertTrue(self.browser.is_text_present('OUR CRAZY FUND-RACERS'))
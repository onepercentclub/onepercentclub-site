from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings
from django.utils.unittest.case import skipUnless

from onepercentclub.tests.utils import OnePercentSeleniumTestCase

from apps.campaigns.models import Campaign
from apps.fundraisers.tests.helpers import FundRaiserTestsMixin

from apps.projects.tests.unittests import ProjectTestsMixin

@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
        'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class HomepageTestCase(FundRaiserTestsMixin, ProjectTestsMixin, OnePercentSeleniumTestCase):
    """ Test that the homepage doesn't error out if no/a campaign is available """

    def setUp(self):
        self.projects = dict([(slugify(title), title) for title in [
           u'Mobile payments for everyone 2!', u'Schools for children 2',  u'Women first 2'
        ]])

        User = get_user_model()
        # Create and activate user.
        self.user = User.objects.create_user('johndoe@example.com', 'secret', primary_language='en')

        for slug, title in self.projects.items():
            project = self.create_project(title=title, slug=slug, money_asked=100000, owner=self.user)
            project.projectcampaign.money_donated = 0
            project.projectcampaign.save()

    def test_homepage_without_campaign(self):
        self.visit_homepage()

        self.assertTrue(self.browser.is_text_present('CHOOSE YOUR PROJECT'))

    def test_homepage_with_campaign(self):
        start, end = timezone.now() - timedelta(hours=8), timezone.now() + timedelta(weeks=1)
        Campaign.objects.create(start=start, end=end, title='FooBarCaMpAIgN', target=100000)

        self.project_with_fundraiser = self.create_project(money_asked=50000)
        self.project_with_fundraiser.is_campaign = True
        self.project_with_fundraiser.save()
        self.fundraiser = self.create_fundraiser(self.user, self.project_with_fundraiser)

        self.visit_homepage()
        self.assertTrue(self.browser.is_text_present('OUR CRAZY FUND-RACERS'))
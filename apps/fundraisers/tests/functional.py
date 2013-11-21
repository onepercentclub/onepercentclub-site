from django.utils.unittest.case import skipUnless
from django.conf import settings

from bluebottle.bluebottle_utils.tests import UserTestsMixin
from onepercentclub.tests.utils import OnePercentSeleniumTestCase

from apps.fund.models import DonationStatuses, Donation
from apps.projects.tests.unittests import ProjectTestsMixin

from ..models import FundRaiser
from .helpers import FundRaiserTestsMixin


@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
        'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class FundRaiserSeleniumTest(FundRaiserTestsMixin, ProjectTestsMixin, UserTestsMixin, OnePercentSeleniumTestCase):
    """
    Integration tests for the fundraiser API.
    """
    def setUp(self):
        """
        Create initial data.
        """
        self.project_with_fundraiser = self.create_project(money_asked=50000)
        self.project_without_fundraiser = self.create_project(money_asked=75000)

        self.some_user = self.create_user(password='secret')
        self.another_user = self.create_user(password='secret')

        self.fundraiser = self.create_fundraiser(self.some_user, self.project_with_fundraiser)

        self.project_with_fundraiser_url = '/projects/{0}'.format(self.project_with_fundraiser.slug)
        self.project_without_fundraiser_url = '/projects/{0}'.format(self.project_without_fundraiser.slug)

        self.fundraiser_url = '/fundraiser/{0}'.format(self.fundraiser.pk)
        self.new_fundraiser_url = '/project/{0}/new-fundraiser'.format(self.project_without_fundraiser.slug)

    def test_link_from_project_page_to_create_fundraiser_anonymous(self):
        """
        Test create a fundraiser for a project as anonymous user.
        """
        self.visit_path(self.project_with_fundraiser_url)

        self.browser.find_link_by_partial_text('Become a fundraiser').first.click()

        self.assertTrue(self.browser.is_text_present('NEW FUNDRAISER'))
        self.assertTrue(self.browser.is_text_present('You can only make a fundraiser if you are logged in.'))
        self.assertFalse(self.browser.is_text_present('Amount to raise'))

    def test_link_from_project_page_to_create_fundraiser_authenticated(self):
        """
        Test create a fundraiser for a project as authenticated user.
        """
        self.assertTrue(self.client.login(username=self.some_user.email, password='secret'))

        self.visit_path(self.project_with_fundraiser_url)

        self.browser.find_link_by_partial_text('Become a fundraiser').first.click()

        self.assertTrue(self.browser.is_text_present('NEW FUNDRAISER'))
        self.assertFalse(self.browser.is_text_present('You can only make a fundraiser if you are logged in.'))
        self.assertTrue(self.browser.is_text_present('Amount to raise'))

        self.browser.fill_form_by_label(
            self.browser.find_by_css('form#fundraiser-new'),
            [
                ('Title', 'Run for the cause'),
                ('Description', 'I will run for joy and to help the cause.'),
                ('Amount to raise', '1000'),
                ('Deadline', '11/30/2013'),
            ]
        )

        self.browser.find_link_by_partial_text('CREATE').first.click()

        self.assertEqual(self.browser.url, '{0}/en/#!/fundraiser/2'.format(self.live_server_url))

        self.assertTrue(self.browser.is_text_present('Run for the cause'))

    def test_link_from_project_to_fundraiser_page(self):
        """
        Test navigate from project to fundraise page.
        """
        self.visit_path(self.project_with_fundraiser_url)

        self.browser.find_link_by_href('#!{0}'.format(self.fundraiser_url)).first.click()

        self.assertEqual(self.browser.url, self.fundraiser_url)

        self.assertTrue(self.fundraiser.title != '')
        self.assertTrue(self.browser.is_text_present(self.fundraiser.title))

    def test_fundraise_page(self):
        """
        Test information on fundraise page.
        """
        self.visit_path(self.fundraiser_url)

        self.assertTrue(self.fundraiser.title != '')
        self.assertTrue(self.browser.is_text_present(self.fundraiser.title))

        link = self.browser.find_link_by_partial_text(self.project_with_fundraiser.title)

        # TODO: check link

    def test_fundraise_donation(self):
        """
        Test create donation for fundraise action.
        """
        self.visit_path(self.fundraiser_url)

        self.assertTrue(self.fundraiser.title != '')
        self.assertTrue(self.browser.is_text_present(self.fundraiser.title))

        self.browser.find_link_by_partial_text('SUPPORT').first.click()

        self.assertEqual(self.browser.url, '{0}/en/#!/support/donations'.format(self.live_server_url))

        self.assertTrue(self.browser.is_text_present('SUPPORT'))
        self.assertTrue(self.browser.is_text_present(self.fundraiser.title))
        self.assertTrue(self.browser.is_text_present('TOTAL'))

        self.browser.find_link_by_partial_text('NEXT STEP').first.click()

        self.assertEqual(self.browser.url, '{0}/en/#!/support/details'.format(self.live_server_url))

        # TODO: Test rest of the flow.

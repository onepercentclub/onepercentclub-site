"""
Functional tests using Selenium.

See: ``docs/testing/selenium.rst`` for details.
"""
from django.utils.text import slugify
import time
from django.conf import settings
from django.utils.unittest.case import skipUnless
from bluebottle.bb_projects.models import ProjectPhase

from bluebottle.test.factory_models.accounts import BlueBottleUserFactory
from bluebottle.test.factory_models.projects import ProjectPhaseFactory

from onepercentclub.tests.factory_models.project_factories import OnePercentProjectFactory
from onepercentclub.tests.utils import OnePercentSeleniumTestCase

@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
            'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class PositiveDonationFlow(OnePercentSeleniumTestCase):

    def setUp(self):
        self.init_projects()

        self.projects = dict([(slugify(title), title) for title in [
           u'Mobile payments for everyone 2!', u'Schools for children 2',  u'Women first 2'
        ]])

        self.user = BlueBottleUserFactory.create(email='johndoe@example.com', primary_language='en', first_name='test',
                                                 last_name='testi')
        campaign_phase = ProjectPhase.objects.get(name='Campaign')


        for slug, title in self.projects.items():
            project = OnePercentProjectFactory.create(title=title, slug=slug, owner=self.user, amount_asked=1000, status=campaign_phase)

        self.login(self.user.email, 'testing')

    def tearDown(self):
        self.logout()


    def test_positive_flow_mockdeal(self, lang_code=None):
        """
        Test a positive donation flow for a donation paid with iDeal
        """
        self.visit_path('/projects/schools-for-children-2', lang_code)

        # Assert visual donation elements on project page
        self.assert_css(".amount-donated")
        self.assert_css(".project-fund-amount-slider")

        self.assert_css(".project-status")

        # Bring up the donation modal
        self.wait_for_element_css('a.btn-primary')
        button = self.browser.find_by_css('a.btn-primary')[0]
        button.click()

        # Verify the elements of the donation modal
        self.wait_for_element_css('input.donation-input')
        donation_input = self.browser.find_by_css("input.donation-input").first

        # Make a donation of 10 euros (default is 25)
        donation_input.value = 10
        self.assertEqual(int(donation_input.value), 10)
        self.assert_css(".donation-buttons")
        self.assert_css("#hideMyName")

        # Jump to next step
        self.scroll_to_and_click_by_css(".donate-btn")

        self.assert_css(".payment-tabs")
        self.assert_css(".payment-tab-content")

        # If you select only the li, the click will fail because the modal closes
        ideal_payments = self.browser.find_by_css("li.ideal label")
        ideal_payments[0].click()

        self.assert_css(".ember-select")

        self.browser.select('mockiDealSelect', 'huey')

        self.scroll_to_and_click_by_css(".payment-btn")

        time.sleep(2)

        self.assertTrue(self.browser.is_text_present('This is a Mock Payment Service provider', wait_time=20))

        self.scroll_to_and_click_by_css('a.btn-ok')

        self.assertTrue(self.browser.is_text_present('Thanks for your support', wait_time=30))

        text = 'I made a donation with mockdeal! Good luck!'

        self.assert_css('.wallpost-textarea')
        self.scroll_to_and_click_by_css('.wallpost-textarea')
        self.browser.find_by_css('.wallpost-textarea').type(text)

        self.browser.find_by_css(".wallpost-buttons .btn")[1].click()

        self.assert_css('.wallpost')

        self.assert_css('.wallpost-content')
        wallpost_text = self.browser.find_by_css(".wallpost-content").first.text
        self.assertEqual(wallpost_text, text)

        author = self.browser.find_by_css(".wallpost-author").first.text
        self.assertEqual(author.lower(), self.user.full_name.lower())


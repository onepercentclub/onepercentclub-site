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

        self.user = BlueBottleUserFactory.create()

        campaign_phase = ProjectPhase.objects.get(name='Campaign')
        for title in [u'Mobile payments for everyone!', u'Schools for children',  u'Women first']:
            project = OnePercentProjectFactory.create(title=title, owner=self.user,
                                                      amount_asked=1000, status=campaign_phase)

        self.login(self.user.email, 'testing')

    def test_positive_flow_mockdeal(self, lang_code=None):
        """
        Test a positive donation flow for a donation paid with iDeal
        """
        self.visit_path('/projects/schools-for-children', lang_code)

        # Assert visual donation elements on project page
        self.assert_css(".amount-donated")
        self.assert_css(".project-fund-amount-slider")

        # Bring up the donation modal
        self.wait_for_element_css('a[data-action-type=donate]')
        button = self.browser.find_by_css('a[data-action-type=donate]')[0]
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

        wallpost = self.browser.driver.find_element_by_css_selector('section#wallposts article:first-of-type')

        wallpost_text = wallpost.find_element_by_css_selector('.wallpost-body').text
        self.assertEqual(wallpost_text, text)

        author = wallpost.find_element_by_css_selector(".user-name").text
        self.assertEqual(author.lower(), self.user.full_name.lower())
        

class LoginDonationFlow(OnePercentSeleniumTestCase):

    def setUp(self):
        self.init_projects()

        self.user = BlueBottleUserFactory.create()

        campaign_phase = ProjectPhase.objects.get(name='Campaign')
        for title in [u'Mobile payments for everyone!', u'Schools for children',  u'Women first']:
            project = OnePercentProjectFactory.create(title=title, owner=self.user,
                                                      amount_asked=1000, status=campaign_phase)

        self.visit_path('/projects/schools-for-children')

        # Assert visual donation elements on project page
        self.assert_css(".amount-donated")
        self.assert_css(".project-fund-amount-slider")

        # Bring up the donation modal
        self.assert_css('a[data-action-type="donate"]')
        self.scroll_to_and_click_by_css('a[data-action-type=donate]')

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

    def tearDown(self):
        self.close_modal()

    def test_signup_donation_flow(self):
        """
        Test signup flow for a donation
        """

        user_data = {
            'first_name': 'Bob',
            'last_name': 'Brown',
            'password': 'testing',
            'email': 'bob.brown@com.net'
        }

        # Wait for the signup modal
        self.assert_css("input[type=email]")

        # There should be two email fields in the signup form
        self.assertEqual(len(self.browser.find_by_css('input[type=email]')), 2)

        # Signup
        self.browser.fill('first-name', user_data['first_name'])
        self.browser.fill('last-name', user_data['last_name'])
        self.browser.fill('email', user_data['email'])
        self.browser.fill('email-confirmation', user_data['email'])
        self.browser.fill('password', user_data['password'])

        self.browser.driver.find_element_by_name('signup').click()

        # Assert the payment modal loads
        self.assert_css('.btn.payment-btn')

    def test_login_donation_flow(self):
        """
        Test login flow for a donation
        """

        # Wait for the signup modal
        self.assert_css("input[type=email]")

        # There should be two email fields in the signup form
        self.assertEqual(len(self.browser.find_by_css('input[type=email]')), 2)

        # Load the login modal
        self.browser.driver.find_element_by_link_text('Sign in here.').click()

        # Wait for the user login modal to appear
        self.assert_css('input[name=username]')

        # There should be an username field in the login form
        self.assertEqual(len(self.browser.find_by_css('input[name=username]')), 1)

        # Login as test user
        self.browser.find_by_css('input[name=username]').first.type(self.user.email)
        self.browser.find_by_css('input[name=password]').first.type('testing')
        self.browser.driver.find_element_by_name('login').click()

        # Assert the payment modal loads
        self.assert_css('.btn.payment-btn')
        self.logout()

    def test_guest_donation_flow(self):
        """
        Test guest flow for a donation
        """

        # Wait for the signup modal
        self.assert_css("input[type=email]")

        # There should be two email fields in the signup form
        self.assertEqual(len(self.browser.find_by_css('input[type=email]')), 2)

        # Select guest donation
        self.browser.driver.find_element_by_link_text('donate as guest.').click()

        # Assert the payment modal loads
        self.assert_css('.btn.payment-btn')


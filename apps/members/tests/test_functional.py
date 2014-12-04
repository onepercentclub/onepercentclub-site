from django.conf import settings
from django.utils.unittest.case import skipUnless
from onepercentclub.tests.utils import OnePercentSeleniumTestCase
from django.utils.translation import ugettext as _


@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
        'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class MemberSettingsTests(OnePercentSeleniumTestCase):

    def _simple_login(self, email, password):
        self.visit_homepage()

        # Find the link to the signup button page and click it.
        self.scroll_to_and_click_by_css('.nav-signup-login a')
        self.wait_for_element_css('input[name=username]')

        # Fill in details.
        self.browser.find_by_css('input[name=username]').first.fill(email)
        self.browser.find_by_css('input[type=password]').first.fill(password)

        self.wait_for_element_css("a[name=login]", timeout=2)
        self.scroll_to_and_click_by_css("a[name=login]")

    """ Confirm login fails without email and shows an error message """
    def test_failed_login_missing_email(self):
        self._simple_login('', 'fake')

        # Should see an error message
        self.assert_css('.modal-flash-message', wait_time=2)

    """ Confirm login fails without password and shows an error message """
    def test_failed_login_missing_password(self):
        self._simple_login('fake@fake.fk', '')

        # Should see an error message
        self.assert_css('.modal-flash-message', wait_time=2)

    """ Confirm login failure works """
    def test_failed_login_wrong_credentials(self):
        self._simple_login('fake@example.com', 'fake')

        # Should see an error message
        self.assert_css('.modal-flash-message', wait_time=2)

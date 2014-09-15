from django.conf import settings
from django.utils.unittest.case import skipUnless
from onepercentclub.tests.utils import OnePercentSeleniumTestCase
from django.utils.translation import ugettext as _


@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
        'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class MemberSettingsTests(OnePercentSeleniumTestCase):


    """ Confirm login fails without email and shows an error message """
    def test_failed_login_missing_email(self):
        self.assertFalse(self.login('', 'fake', wait_time=5))

        # Should see an error message
        self.wait_for_element_css('.modal-flash-message.error', timeout=20)
        self.scroll_to_and_click_by_css('modal-fullscreen-close')

    """ Confirm login fails without password and shows an error message """
    def test_failed_login_missing_password(self):
        self.assertFalse(self.login('fake@fake.fk', '', wait_time=5))

        # Should see an error message
        self.wait_for_element_css('.modal-flash-message.error', timeout=20)
        self.scroll_to_and_click_by_css('modal-fullscreen-close')

    """ Confirm login failure works """
    def test_failed_login_wrong_credentials(self):
        self.browser.reload()
        self.assertFalse(self.login('fake@example.com', 'fake', wait_time=5))

        # Should see an error message
        self.wait_for_element_css('.modal-flash-message.error', timeout=20)
        self.scroll_to_and_click_by_css('modal-fullscreen-close')

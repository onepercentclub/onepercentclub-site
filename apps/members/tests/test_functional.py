from django.conf import settings
from django.utils.unittest.case import skipUnless
from onepercentclub.tests.utils import OnePercentSeleniumTestCase
from django.utils.translation import ugettext as _


@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
        'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class MemberSettingsTests(OnePercentSeleniumTestCase):

    """ Confirm login fails without email and shows an error message """
    def test_failed_login_missing_email(self):
        self.login('', 'fake', wait_time=10)

        # Should see an error message
        self.assert_css('.modal-flash-message', wait_time=10)
        self.assert_text(_("Email required"))

    """ Confirm login fails without password and shows an error message """
    def test_failed_login_missing_password(self):
        self.login('fake@fake.fk', '', wait_time=10)

        # Should see an error message
        self.assert_css('.modal-flash-message', wait_time=10)
        self.assert_text(_("Password required"))

    """ Confirm login failure works """
    def test_failed_login_wrong_credentials(self):
        self.assertFalse(self.login('fake@example.com', 'fake', wait_time=10))

        # Should see an error message
        # self.assert_css('.modal-flash-message', wait_time=10)

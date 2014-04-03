from django.conf import settings
from django.utils.unittest.case import skipUnless
from onepercentclub.tests.utils import OnePercentSeleniumTestCase


@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
        'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class MemberSettingsTests(OnePercentSeleniumTestCase):
    pass
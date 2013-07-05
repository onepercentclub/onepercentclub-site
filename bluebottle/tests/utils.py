from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.db import transaction
from django.test import LiveServerTestCase
from django.test.testcases import connections_support_transactions, disable_transaction_methods, restore_transaction_methods

from splinter import Browser


def css_dict(style):
    """
    Returns a dict from a style attribute value.

    Usage::

        >>> css_dict('width: 2.2857142857142856%; overflow: hidden;')
        {'overflow': 'hidden', 'width': '2.2857142857142856%'}

        >>> css_dict('width:2.2857142857142856%;overflow:hidden')
        {'overflow': 'hidden', 'width': '2.2857142857142856%'}

    """
    if not style:
        return {}

    try:
        return dict([(k.strip(), v.strip()) for k, v in [prop.split(':') for prop in style.rstrip(';').split(';')]])
    except ValueError, e:
        raise ValueError('Could not parse CSS: %s (%s)' % (style, e))


class SeleniumTestCase(LiveServerTestCase):
    """
    Selenium test cases should inherit from this class.

    Wrapper around ``LiveServerTestCase`` to provide a standard browser instance. In addition it performs some tests to
    make sure all settings are correct.
    """

    @classmethod
    def setUpClass(cls):
        """
        Prepare the test class rather then doing this for every individual test.
        """
        if not hasattr(settings, 'SELENIUM_WEBDRIVER'):
            raise ImproperlyConfigured('Define SELENIUM_WEBDRIVER in your settings.py.')

        cls.browser = Browser(settings.SELENIUM_WEBDRIVER)

        super(SeleniumTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        """
        Make sure the browser quits afterwards.
        """
        super(SeleniumTestCase, cls).tearDownClass()

        cls.browser.quit()

    def _fixture_setup(self):
        """
        Implement the same logic as ``django.test.TestCase`` to make fixture loading more smooth.
        """
        if not connections_support_transactions():
            return super(SeleniumTestCase, self)._fixture_setup()

        assert not self.reset_sequences, 'reset_sequences cannot be used on TestCase instances'

        for db_name in self._databases_names():
            transaction.enter_transaction_management(using=db_name)
            transaction.managed(True, using=db_name)
        disable_transaction_methods()

        from django.contrib.sites.models import Site
        Site.objects.clear_cache()

        for db in self._databases_names(include_mirrors=False):
            if hasattr(self, 'fixtures'):
                call_command('loaddata', *self.fixtures,
                             **{
                                'verbosity': 0,
                                'commit': False,
                                'database': db,
                                'skip_validation': True,
                             })

    def _fixture_teardown(self):
        """
        Implement the same logic as ``django.test.TestCase`` to make fixture loading more smooth.
        """
        if not connections_support_transactions():
            return super(SeleniumTestCase, self)._fixture_teardown()

        restore_transaction_methods()
        for db in self._databases_names():
            transaction.rollback(using=db)
            transaction.leave_transaction_management(using=db)

    def login(self, username, password):
        self.visit_homepage()

        # Find the link to the signup button page and click it.
        self.browser.find_link_by_text('Login').first.click()

        # Validate that we are on the intended page.
        if not self.browser.is_text_present('LOG IN', wait_time=10):
            return False

        # Fill in details.
        self.browser.fill('username', username)
        self.browser.fill('password', password)

        self.browser.find_by_value('Login').first.click()

        return self.browser.is_text_present('MY 1%', wait_time=10)

    def visit_path(self, path, lang_code=None):
        if lang_code is None:
            lang_code = 'en'

        if path and not path.startswith('#'):
            path = '#%s' % path

        # Open the homepage (always the starting point), in English.
        return self.browser.visit('%(url)s/%(lang_code)s/%(path)s' % {
            'url': self.live_server_url,
            'lang_code': lang_code,
            'path': path
        })

    def visit_homepage(self, lang_code=None):
        """
        Convenience function to open the homepage.
        """
        # Open the homepage, in the specified language.
        self.visit_path('', lang_code)

        # # Check if the homepage opened, and the dynamically loaded content appeared.
        # # Remember that
        # self.assertTrue(self.browser.is_text_present('CHOOSE YOUR PROJECT', wait_time=10),
        #         'Cannot load the homepage. Did you load any data fixtures for testing?')
        return self.browser.is_element_present_by_id('title', wait_time=10)

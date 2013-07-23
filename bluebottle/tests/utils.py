import time
import urlparse

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import LiveServerTestCase

from splinter.browser import _DRIVERS
from splinter.element_list import ElementList
from splinter.exceptions import DriverNotFoundError

from apps.projects.models import Project


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

def BrowserExt(driver_name='firefox', *args, **kwargs):
    """
    Small helper to combine the correct webdriver with some additional methods without cloning the project.
    """
    try:
        driver_class = _DRIVERS[driver_name]
    except KeyError:
        raise DriverNotFoundError("No driver for %s" % driver_name)

    class DriverClassExt(driver_class):
        """
        This class is an extension that overrides certain functions to allow custom behaviour.
        """
        def visit(self, url):
            """
            Visit and wait for redirect. Also performs the redirect.
            """
            super(DriverClassExt, self).visit(url)
            
            if self.driver_name == 'PhantomJS':
                time.sleep(3) # Allow the page to load correctly.

                if self.status_code.code in [302, 301]:
                    loc = self.response.msg['Location']
                    redirect_url = urlparse.urlparse(loc)
                    parsed_url = urlparse.urlparse(self.request_url)
            
                    # Build new absolute URL.
                    absolute_url = urlparse.urlunparse([
                            redirect_url.scheme,
                            redirect_url.netloc,
                            redirect_url.path,
                            redirect_url.params,
                            redirect_url.query,
                            parsed_url.fragment
                            ])
                    self.visit(absolute_url)

    new_class = type('BrowserExt', (DriverClassExt, WebDriverAdditionMixin), {})

    if driver_name == 'PhantomJS':
        kwargs.update({'load_images': False})

    return new_class(*args, **kwargs)


class WebDriverAdditionMixin(object):
    """
    Additional helper methods for the web driver.
    """
    def fill_form_by_css(self, form, data):
        """
        Fills in a form by finding input elements by CSS.

        :param form: The form ``WebElement``.
        :param data: A dict in the form ``{'input css': 'value'}``.
        """

        if not isinstance(data, dict):
            raise RuntimeError('Argument data must be dict.')

        # Fill in the form.
        for css, val in data.items():
            form.find_by_css(css).first.fill(val)

    def fill_form_by_label(self, form, data):
        """
        Fills in a form by finding labels.

        NOTE: This function works best if you define all labels and input elements in your data.

        :param form: The form ``WebElement``.
        :param data: List of tuples in the form ``[('label', 'value'), ...]``. The value can also be a list if multiple
                     inputs are connected to a single label.

        Example::

            # ...
            self.fill_form_by_label(
                self.browser.find_by_tag('form'),
                [
                    ('Name', ['John', 'Doe']),
                    ('Email', 'johndoe@onepercentclub.com'),
                ]
            )

        """
        if not isinstance(data, list):
            raise RuntimeError('Argument data must be a list of tuples.')

        labels = form.find_by_tag('label')
        inputs = form.find_by_css('input, textarea, select')

        # Fill in the form. Keep an offset for if multiple inputs are used.
        offset = 0
        for label_text, values in data:
            if not isinstance(values, list):
                values = [values]

            for index, form_label in enumerate(labels):
                if form_label.text.strip('\r\n ') == label_text:
                    for i, val in enumerate(values):
                        offset += i

                        if val is None:
                            continue

                        form_input = inputs[index + offset]
                        form_input_tag_name = form_input.tag_name

                        if form_input_tag_name == 'input':
                            form_input_type = form_input['type']

                            if form_input_type == 'file':
                                form_input.attach_file(val)
                            elif form_input_type == 'checkbox':
                                if val:
                                    form_input.check()
                                else:
                                    form_input.uncheck()
                            elif form_input_type == 'radio':
                                radio_group = form_input['name']
                                self.choose(radio_group, val)
                            else:
                                form_input.fill(val)
                        elif form_input_tag_name == 'select':
                            # Workaround for form_input.select(val) which uses the name attribute to find the options.
                            # However, some select elements do not have a name attribute.
                            # TODO: Report issue found in Splinter 0.5.3
                            for option in form_input.find_by_tag('option'):
                                if option['value'] == val:
                                    option.click()
                                    break
                        else:
                            form_input.fill(val)
                    break

    def find_link_by_itext(self, text, exact=False):
        """
        Finds a link by text in a more robust way than the default method. Also allows for case sensitive and
        insensitive matches.

        :param text: The text to search for within a link element.
        :param exact: ``True`` if the match mut be an exact match. ``False`` (default) for case insensitive matches.

        :return: List of matching elements.
        """
        result = []
        for link in self.find_by_css('a, button, input[type="button"], input[type="submit"]'):
            if link.text == text or (not exact and link.text.lower() == text.lower()):
                result.append(link)
        return ElementList(result, find_by='link by itext', query=text)


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

        cls.browser = BrowserExt(settings.SELENIUM_WEBDRIVER, wait_time=10)

        super(SeleniumTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        """
        Make sure the browser quits afterwards.
        """
        cls.browser.quit()

        super(SeleniumTestCase, cls).tearDownClass()

    def _post_teardown(self):
        """
        Allow PhantomJS to close down properly after a test. It can still perform requests after the last test statement
        was made. 
        """
        time.sleep(3)

        super(SeleniumTestCase, self)._post_teardown()

    def login(self, username, password):
        """
        Perform login operation on the website.

        :param username: The user's email address.
        :param password: The user's password
        :return: ``True`` if login was successful.
        """
        self.visit_homepage()

        # Find the link to the signup button page and click it.
        self.browser.find_link_by_text('Log in').first.click()

        # Validate that we are on the intended page.
        if not self.browser.is_text_present('LOG IN', wait_time=10):
            return False

        # Fill in details.
        self.browser.fill('username', username)
        self.browser.fill('password', password)

        self.browser.find_by_value('Log in').first.click()

        return self.browser.is_text_present('MY 1%', wait_time=10)

    def visit_path(self, path, lang_code=None):
        """
        Visits a relative path of the website.

        :param path: The relative URL path.
        :param lang_code: A two letter language code as used in the URL.
        """
        if lang_code is None:
            lang_code = 'en'

        if path and not path.startswith('#!'):
            path = '#!%s' % path

        # Open the homepage (always the starting point), in English.
        return self.browser.visit('%(url)s/%(lang_code)s/%(path)s' % {
            'url': self.live_server_url,
            'lang_code': lang_code,
            'path': path
        })        

    def visit_homepage(self, lang_code=None):
        """
        Convenience function to open the homepage.

        :param lang_code: A two letter language code as used in the URL.
        :return: ``True`` if the homepage could be visited.
        """
        # TODO: A project should not be needed to visit the homepage.
        self.assertNotEqual(Project.objects.count(), 0,
                            'The homepage depends on at least 1 project to be present to prevent JS errors.')

        # Open the homepage, in the specified language.
        self.visit_path('', lang_code)

        # # Check if the homepage opened, and the dynamically loaded content appeared.
        # # Remember that
        return self.browser.is_text_present('CHOOSE YOUR PROJECT', wait_time=10)


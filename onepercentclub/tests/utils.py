import json
from onepercentclub.tests.factory_models.project_factories import PartnerFactory
import os
import requests
import base64
from bluebottle.bb_projects.models import ProjectPhase, ProjectTheme
from bluebottle.test.factory_models.projects import ProjectPhaseFactory, ProjectThemeFactory
from bluebottle.test.utils import SeleniumTestCase
from bluebottle.utils.models import Language
from django.test import TestCase
from bluebottle.test.factory_models.utils import LanguageFactory


class InitProjectDataMixin(object):

    def init_projects(self):
        """
        Set up some basic models needed for project creation.
        """
        phase_data = [{'id': 1, 'name': 'Plan - New', 'viewable': False},
                      {'id': 2, 'name': 'Plan - Submitted', 'viewable': False},
                      {'id': 3, 'name': 'Plan - Needs Work', 'viewable': False},
                      {'id': 4, 'name': 'Plan - Rejected', 'viewable': False},
                      {'id': 6, 'name': 'Plan - Accepted', 'viewable': True},
                      {'id': 5, 'name': 'Campaign', 'viewable': True},
                      {'id': 7, 'name': 'Stopped', 'viewable': False},
                      {'id': 8, 'name': 'Done - Complete', 'viewable': True},
                      {'id': 9, 'name': 'Done - Incomplete', 'viewable': True}]

        theme_data = [{'id': 1, 'name': 'Education'},
                      {'id': 2, 'name': 'Environment'}]

        language_data = [{'id': 1, 'code': 'en', 'language_name': 'English', 'native_name': 'English'},
                         {'id': 2, 'code': 'nl', 'language_name': 'Dutch', 'native_name': 'Nederlands'}]

        partner_data = [{'id': 1, 'slug': 'cheetah', 'name': 'The Cheetah Campaign'},
                        {'id': 2, 'slug': 'macro_micro', 'name': 'Macro Micro'}]

        for partner in partner_data:
            PartnerFactory.create(**partner)

        for phase in phase_data:
            ProjectPhaseFactory.create(**phase)

        for theme in theme_data:
            ProjectThemeFactory.create(**theme)

        for language in language_data:
            LanguageFactory.create(**language)


class OnePercentTestCase(InitProjectDataMixin, TestCase):
    pass


class OnePercentSeleniumTestCase(InitProjectDataMixin, SeleniumTestCase):

    def login(self, username, password, wait_time=30):
        """
        Perform login operation on the website.

        :param username: The user's email address.
        :param password: The user's password
        :return: ``True`` if login was successful.
        """
        self.init_projects()
        self.visit_homepage()

        if self.browser.is_text_present('My 1%'):
            self.logout()
            self.wait_for_element_css('.nav-signup-login a')

        # Find the link to the signup button page and click it.
        self.scroll_to_and_click_by_css('.nav-signup-login a')
        self.wait_for_element_css('.modal-fullscreen-content')

        # Fill in details.
        self.browser.find_by_css('input[name=username]').first.fill(username)
        self.browser.find_by_css('input[type=password]').first.fill(password)

        self.wait_for_element_css("a[name=login]", timeout=10)
        self.scroll_to_and_click_by_css("a[name=login]")

        return self.browser.is_text_present('My 1%', wait_time=wait_time)

    def logout(self):
        return self.visit_path("/logout")

    def tearDown(self):
        # Navigate to homepage before tearing the browser down.
        # This helps Travis.
        self.visit_homepage()

    def visit_homepage(self, lang_code=None):
        """
        Convenience function to open the homepage.

        :param lang_code: A two letter language code as used in the URL.
        :return: ``True`` if the homepage could be visited.
        """
        self.visit_path('', lang_code)

        # Check if the homepage opened, and the dynamically loaded content appeared.
        return self.wait_for_element_css('#home')

    def visit_path(self, path, lang_code=None):
        if lang_code is None:
            lang_code = 'en'
        if path and not path.startswith('#!'):
            path = '#!%s' % path

        url = '%(url)s/%(lang_code)s/%(path)s' % {
            'url': self.live_server_url,
            'lang_code': lang_code,
            'path': path
        }

        self.browser.driver.get(url)
        
        # TODO: maybe we can do an element check here - method caller would 
        #       pass a css element to check before returning a success.
        return True

    def scroll_to_by_css(self, selector):
        """
        Overwrite this function so the elements don't scroll behind the top menu.
        """

        element = self.wait_for_element_css(selector)

        if element:
            y = int(element.location['y']) - 100
            x = int(element.location['x'])
            self.browser.execute_script("window.scrollTo(%s,%s)" % (x, y))

        return element

    def upload_screenshot(self):
        client_id = os.environ.get('IMGUR_CLIENT_ID')
        client_key = os.environ.get('IMGUR_CLIENT_SECRET')

        if client_id and client_key:
            client_auth = 'Client-ID {0}'.format(client_id)
            headers = {'Authorization': client_auth}
            url = 'https://api.imgur.com/3/upload.json'
            filename = '/tmp/screenshot.png'

            print 'Attempting to save screenshot...'
            self.browser.driver.save_screenshot(filename)

            response = requests.post(
                url,
                headers = headers,
                data = {
                    'key': client_key,
                    'image': base64.b64encode(open(filename, 'rb').read()),
                    'type': 'base64',
                    'name': filename,
                    'title': 'Travis Screenshot'
                }
            )

            print 'Uploaded screenshot:'
            data = json.loads(response.content)
            print data['data']['link']
            print response.content

        else:
            print 'Imgur API keys not found!'


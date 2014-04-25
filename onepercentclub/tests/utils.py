from bluebottle.test.factory_models.projects import ProjectPhaseFactory
from bluebottle.test.utils import SeleniumTestCase
from django.test import TestCase
from onepercentclub.tests.factory_models.project_factories import OnePercentProjectFactory


class OnePercentTestCase(TestCase):

    def init_projects(self):
        OnePercentProjectFactory.init_related_models()


class OnePercentSeleniumTestCase(SeleniumTestCase):

    def init_projects(self):
        OnePercentProjectFactory.init_related_models()

    def login(self, username, password):
        """
        Perform login operation on the website.

        :param username: The user's email address.
        :param password: The user's password
        :return: ``True`` if login was successful.
        """
        self.init_projects()
        self.visit_homepage()

        # Find the link to the signup button page and click it.
        self.browser.find_link_by_itext('log in').first.click()

        # Validate that we are on the intended page.
        if not self.browser.is_text_present('LOG IN', wait_time=10):
            return False

        # Fill in details.
        self.browser.fill('username', username)
        self.browser.fill('password', password)

        self.browser.find_by_value('Login').first.click()

        return self.browser.is_text_present('MY 1%', wait_time=10)

    def logout(self):
        return self.browser.visit('%(url)s/en/accounts/logout/' % {
            'url': self.live_server_url
        })

    def visit_homepage(self, lang_code=None):
        """
        Convenience function to open the homepage.

        :param lang_code: A two letter language code as used in the URL.
        :return: ``True`` if the homepage could be visited.
        """
        self.visit_path('', lang_code)

        # # Check if the homepage opened, and the dynamically loaded content appeared.
        return self.wait_for_element_css('#home')

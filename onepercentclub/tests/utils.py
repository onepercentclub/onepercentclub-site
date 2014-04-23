from bluebottle.test.factory_models.projects import ProjectPhaseFactory
from bluebottle.test.utils import SeleniumTestCase


class OnePercentSeleniumTestCase(SeleniumTestCase):
    def login(self, username, password):
        """
        Perform login operation on the website.

        :param username: The user's email address.
        :param password: The user's password
        :return: ``True`` if login was successful.
        """
        # We need some project phases to get things going
        phase = ProjectPhaseFactory.create(name='Campaign')
        phase = ProjectPhaseFactory.create(name='Plan Submitted')

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

    def visit_homepage(self, lang_code=None):
        """
        Convenience function to open the homepage.

        :param lang_code: A two letter language code as used in the URL.
        :return: ``True`` if the homepage could be visited.
        """

        self.visit_path('', lang_code)

        # # Check if the homepage opened, and the dynamically loaded content appeared.
        # # Remember that
        return self.browser.is_text_present('CHOOSE YOUR PROJECT', wait_time=10)

    def assertDatePicked(self):
        # Pick a deadline next month
        self.assertTrue(self.scroll_to_and_click_by_css(".hasDatepicker"))

        # Wait for date picker popup
        self.assertTrue(self.browser.is_element_present_by_css("#ui-datepicker-div"))

        # Click Next to get a date in the future
        self.browser.find_by_css("[title=Next]").first.click()
        self.assertTrue(self.browser.is_text_present("10"))
        self.browser.find_link_by_text("10").first.click()

    def scroll_to_and_click_by_css(self, selector):
        if self.browser.is_element_present_by_css(selector):
            element = self.browser.driver.find_element_by_css_selector(selector)
            self.browser.execute_script("window.scrollTo(0,%s)" % element.location['y']);
            element.click()
            return True
        else:
            return False

    def assert_css(self, selector, wait_time=5):
        return self.assertTrue(self.browser.is_element_present_by_css(selector, wait_time=wait_time) )

    def assert_text(self, text, wait_time=5):
        return self.assertTrue(self.browser.is_text_present(text, wait_time=wait_time) )

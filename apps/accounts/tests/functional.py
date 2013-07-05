# -*- coding: utf8 -*-
"""
Functional tests using Selenium.

See: ``docs/testing/selenium.rst`` for details.
"""
import time
import re

from django.contrib.sites.models import Site
from django.conf import settings
from django.core import mail
from django.utils.unittest.case import skipUnless, skipIf

from bluebottle.tests.utils import SeleniumTestCase, css_dict
from ..models import BlueBottleUser
from selenium.webdriver import ActionChains


@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
        'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class MemberSignupSeleniumTests(SeleniumTestCase):
    """
    Selenium tests for member signup.
    """
    #fixtures = ['demo',]

    def setUp(self):
        pass

    def test_signup(self):
        """
        Test become member signup.

        1. Visit signup page
        2. Fill in form
        3. Click signup button
        4. Receive activation link by mail
        5. Visit activation link
        6. Validate that user is active
        """
        self.visit_homepage()

        # Find the link to the signup button page and click it.
        self.browser.find_link_by_partial_text('Signup').first.click()

        # Validate that we are on the intended page.
        self.assertTrue(self.browser.is_text_present('BECOME A 1%MEMBER', wait_time=10),
                'Cannot load the signup page.'),

        self.assertEqual(self.browser.url, '%s/en/#/signup' % self.live_server_url)
        self.assertEqual(self.browser.title, '1%Club')

        # NOTE: Most ember elements don't have meaningfull names. This makes it hard to find out which element is the
        # correct one.
        form = self.browser.find_by_css('form.form-signup').first

        # Fill in the form.
        form_data = {
            'input[placeholder="First name"]': 'John',
            'input[placeholder="Surname"]': 'Doe',
            'input[type="email"]': 'johndoe@example.com',
            'input[type="password"]': 'secret'
        }
        self.fill_form_by_css(form, form_data)

        # Make sure we have an empty mailbox and the user doesn't exist yet.
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(BlueBottleUser.objects.filter(email='johndoe@example.com').count(), 0)

        # Click the signup button within the form.
        form.find_by_css('button').first.click()

        # After signing up, a message should appear
        self.assertTrue(self.browser.is_text_present('THANKS FOR SIGNING UP!', wait_time=10))

        # And a user should be created.
        self.assertEqual(BlueBottleUser.objects.filter(email='johndoe@example.com').count(), 1)
        user = BlueBottleUser.objects.get(email='johndoe@example.com')
        self.assertFalse(user.is_active)

        # And a mail should be sent to the just signed up email address.
        self.assertEqual(len(mail.outbox), 1)
        activation_mail = mail.outbox[0]

        self.assertEqual(activation_mail.subject, 'Welcome to 1%CLUB')
        self.assertIn(user.email, activation_mail.to)

        # Extract activation link and change domain for the test.
        activation_link = re.findall('href="([a-z\.\/\#]+/activate\/[^"]+)', activation_mail.body)[0]
        current_site = Site.objects.get_current()
        self.assertTrue(activation_link.startswith(current_site.domain))
        activation_link = activation_link.replace(Site.objects.get_current().domain, self.live_server_url)

        # Visit the activation link.
        self.browser.visit(activation_link)

        # TODO: Can't see any message about it on the web site after clicking the link.
        # TODO: After visiting the link, the website is shown in Dutch again.
        self.assertTrue(self.browser.is_element_present_by_id('title', wait_time=10))
        time.sleep(1)

        # Reload the user.
        user = BlueBottleUser.objects.get(pk=user.pk)
        self.assertTrue(user.is_active)

    def test_login(self):
        """
        Test user can login.
        """
        # Create and activate user.
        user = BlueBottleUser.objects.create_user('johndoe@example.com', 'secret')

        self.visit_homepage()

        # Find the link to the signup button page and click it.
        self.browser.find_link_by_text('Login').first.click()

        # Validate that we are on the intended page.
        self.assertTrue(self.browser.is_text_present('LOG IN', wait_time=10),
                'Cannot load the login popup.'),

        # Fill in details.
        self.browser.fill('username', user.email)
        self.browser.fill('password', 'secret')

        self.browser.find_by_value('Login').first.click()

        self.assertTrue(self.browser.is_text_present('MY 1%', wait_time=10))

    @skipIf(settings.SELENIUM_WEBDRIVER=='firefox', 'Firefox does not support mouse interactions.')
    def test_edit_profile(self):
        # Create and activate user.
        user = BlueBottleUser.objects.create_user('johndoe@example.com', 'secret')
        
        self.login(user.email, 'secret')

        self.browser.find_by_css('.nav-member-my1percent').first.mouse_over()
        self.browser.find_link_by_partial_text('Edit my profile & settings').first.click()

        # Validate that we are on the intended page.
        self.assertTrue(self.browser.is_text_present('EDIT YOUR PROFILE', wait_time=10))

        form = self.browser.find_by_tag('form').first

        # Fill in the form.
        form_data = [
            ('Name', ['John', 'Doe']),
            ('Profile Picture', None),
            ('About Yourself', 'I am John Doe.'),
            ('Why are you a member?', 'Because I care.'),
            ('Your website', 'http://www.onepercentclub.com'),
            ('Location', 'Amsterdam'),
            ('Time available', '5-8_hours_week')
        ]
        self.fill_form_by_label(form, form_data)

        form.find_by_css('button').first.click()

        # Validate with the message.
        self.assertTrue(self.browser.is_text_present('Profile saved', wait_time=10))

        # Reload the user.
        user = BlueBottleUser.objects.get(pk=user.pk)
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.about, 'I am John Doe.')
        self.assertEqual(user.why, 'Because I care.')
        self.assertEqual(user.website, 'http://www.onepercentclub.com')
        self.assertEqual(user.location, 'Amsterdam')
        self.assertEqual(user.availability, '5-8_hours_week')

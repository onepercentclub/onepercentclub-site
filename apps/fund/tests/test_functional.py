# -*- coding: utf-8 -*-
"""
Functional tests using Selenium.

See: ``docs/testing/selenium.rst`` for details.
"""
import time
from bluebottle.bb_projects.models import ProjectPhase

from django.conf import settings
from django.utils.text import slugify
from django.utils.unittest.case import skipUnless
from onepercentclub.tests.factory_models.donation_factories import DonationFactory
from onepercentclub.tests.utils import OnePercentSeleniumTestCase

from bluebottle.test.factory_models.accounts import BlueBottleUserFactory
from onepercentclub.tests.factory_models.project_factories import OnePercentProjectFactory


@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
            'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class DonationSeleniumTests(OnePercentSeleniumTestCase):
    """
    Selenium tests for Projects.
    """

    fixtures = ['region_subregion_country_data.json'] # apps/geo/fixtures/

    def setUp(self):

        self.init_projects()
        self.phase_campaign = ProjectPhase.objects.get(slug='campaign')

        self._projects = []
        self.projects = dict([(slugify(title), title) for title in [
            u'Women first', u'Mobile payments for everyone!', u'Schools for children'
        ]])

        for slug, title in self.projects.items():
            project = OnePercentProjectFactory.create(title=title, slug=slug, amount_asked=500)
            self._projects.append(project)

            project.amount_donated = 500  # EUR 5.00
            project.status = self.phase_campaign
            project.save()

        self.some_user = BlueBottleUserFactory.create()
        self.another_user = BlueBottleUserFactory.create()

        self.donate_details = {'firstname': 'Pietje',
                               'lastname': 'Paulusma',
                               'email': 'pietje@example.com',
                               'address': 'Herengracht 416',
                               'postcode': '1017BZ',
                               'city': 'Amsterdam',
                               'country': 'NL'}

    def visit_project_list_page(self, lang_code=None):
        self.visit_path('/projects', lang_code)

        self.assertTrue(self.browser.is_element_present_by_css('.project-item'),
                        'Cannot load the project list page.')

    def test_view_project_page_with_donation(self):
        """
        Test project donation by an anonymous user
        """
        self.visit_path('/projects/women-first')
        self.assertTrue(self.browser.is_text_present('WOMEN FIRST', wait_time=10))
        self.assertEqual(self.browser.find_by_css('h1.project-title').first.text, u'WOMEN FIRST')

        donation_status_text = self.browser.find_by_css('.project-fund-amount').first.text

        self.assertTrue(u'SUPPORT PROJECT' in self.browser.find_by_css('div.project-action').first.text)

        # Click through to the support-page, check the default values and
        # verify we are donating to the correct project
        self.browser.find_by_css('div.project-action a').first.click()

        self.assertTrue(self.browser.is_text_present('LIKE TO GIVE', wait_time=10))

        self.assertEqual(self.browser.find_by_css('h2.project-title').first.text[:11], u'WOMEN FIRST')

        self.assertEqual(self.browser.find_by_css('.fund-amount-control label').first.text, u"I'D LIKE TO GIVE")
        self.assertTrue(u'500' in self.browser.find_by_css('.fund-amount-needed').first.text)
        input_field = self.browser.find_by_css('.fund-amount-input').first
        self.assertEqual(input_field['value'], u'20')

        # Change the amount we want to donate

        # TODO: Verify we can change the amount to donate, this currently
        # doesn't work properly via Selenium: Doing the following gives me a 500:
        # TypeError: Cannot convert None to Decimal.

        # input_field.click()
        # input_field.fill(40)

        # TODO: Currently two donation-entries are added by default... I'm not sure why

        # Check the total and make sure there is only one donation entry
        # self.assertTrue(self.browser.find_by_css('.donation-total .currency').first.text.find(' 20') != -1)
        # self.assertTrue(len(self.browser.find_by_css('ul#donation-projects li.donation-project')) == 1)

        # Continue with our donation, fill in the details

        self.browser.find_by_css('.btn-next').first.click()
        self.assertTrue(self.browser.is_text_present('Your full name', wait_time=1))

        # NOTE: making use of fill_form_by_css() might be a better idea

        fields = self.browser.find_by_css('input[type=text]')
        firstname = fields[0]
        lastname = fields[1]
        email = fields[2]
        address = fields[3]
        postcode = fields[4]
        city = fields[5]

        self.assertEqual(firstname['placeholder'], u'First name')
        self.assertEqual(lastname['placeholder'], u'Last name')
        self.assertEqual(email['placeholder'], u'Email')
        self.assertEqual(address['placeholder'], u'Address')
        self.assertEqual(postcode['placeholder'], u'Postal code')
        self.assertEqual(city['placeholder'], u'City')

        firstname.fill(self.donate_details['firstname'])
        lastname.fill(self.donate_details['lastname'])
        email.fill(self.donate_details['email'])
        address.fill(self.donate_details['address'])
        postcode.fill(self.donate_details['postcode'])
        city.fill(self.donate_details['city'])

        # Click on the NEXT button
        self.browser.find_by_css('button.btn-next').first.click()

        # FIXME: These tests fail on Travis.
        # self.assertTrue(self.browser.is_element_present_by_css('.btn-skip', wait_time=5))
        #
        # # Don't sign up. Skip this form.
        # self.browser.find_by_css('.btn-skip').first.click()
        #
        # self.assertTrue(self.browser.is_text_present("YOU'RE ALMOST THERE!", wait_time=5))
        #
        # # Proceed with the payment
        # # Select Ideal + ABN Amro for payment
        # time.sleep(2)
        #
        # self.scroll_to_and_click_by_css('.tabs-vertical .radio')
        # self.scroll_to_and_click_by_css('.fund-payment-item .radio')

    def test_donation_thank_you_page(self):

        self.assertTrue(self.login(username=self.some_user.email, password='testing'))

        # Create dummy donation, so we can validate the thank you page.
        donation = DonationFactory.create(user=self.some_user, project=self._projects[0])
        donation.order.status = 'current'
        donation.order.user = self.some_user
        donation.order.closed = None

        from apps.cowry_docdata.models import DocDataPaymentOrder
        DocDataPaymentOrder.objects.create(order=donation.order, payment_order_id='dummy')

        donation.order.save()

        self.visit_path('/support/thanks/{0}'.format(donation.order.pk))


        # Validate thank you page.
        self.assertTrue(self.browser.is_text_present('WELL, YOU ROCK!'))
        self.assertTrue(self.browser.is_text_present(self._projects[0].title.upper()))

        # check that the correct links are present
        self.browser.find_by_css('li.project-list-item a').first.click()
        self.assertEqual(self.browser.url, '{0}/en/#!/projects/{1}'.format(self.live_server_url, self._projects[0].slug))

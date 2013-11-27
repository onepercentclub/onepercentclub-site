# -*- coding: utf-8 -*-
"""
Functional tests using Selenium.

See: ``docs/testing/selenium.rst`` for details.
"""
import time

from django.conf import settings
from django.utils.text import slugify
from django.utils.unittest.case import skipUnless

from apps.fund.models import DonationStatuses, Donation, OrderStatuses
from apps.donations.tests.helpers import DonationTestsMixin
from .unittests import ProjectTestsMixin, UserTestsMixin

from onepercentclub.tests.utils import OnePercentSeleniumTestCase


@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
            'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class DonationSeleniumTests(DonationTestsMixin, ProjectTestsMixin, UserTestsMixin, OnePercentSeleniumTestCase):
    """
    Selenium tests for Projects.
    """

    fixtures = ['region_subregion_country_data.json'] # apps/geo/fixtures/

    def setUp(self):
        self._projects = []
        self.projects = dict([(slugify(title), title) for title in [
            u'Women first', u'Mobile payments for everyone!', u'Schools for children'
        ]])

        for slug, title in self.projects.items():
            project = self.create_project(title=title, slug=slug, money_asked=50000)  # EUR 500.00
            self._projects.append(project)

            project.projectcampaign.money_donated = 500  # EUR 5.00
            project.projectcampaign.save()
            project.phase = 'campaign'

        self.some_user = self.create_user()
        self.another_user = self.create_user()

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
        self.visit_project_list_page()

        # Besides the waiting for JS to kick in, we also need to wait for the funds raised animation to finish.
        time.sleep(2)

        # Click through to the project and verify we can support the project
        # and the fundraising values we expect

        self.browser.find_by_css('span.project-header').first.click()  # First project in the list
        self.assertTrue(self.browser.is_text_present('WOMEN FIRST', wait_time=10))
        self.assertEqual(self.browser.find_by_css('h1.project-title').first.text, u'WOMEN FIRST')

        donation_status_text = self.browser.find_by_css('.project-fund-amount').first.text

        self.assertTrue(u'SUPPORT PROJECT' in self.browser.find_by_css('div.project-action').first.text)

        # Click through to the support-page, check the default values and
        # verify we are donating to the correct project
        self.browser.find_by_css('div.project-action a').first.click()

        self.assertTrue(self.browser.is_text_present('LIKE TO GIVE', wait_time=10))

        self.assertEqual(self.browser.find_by_css('h2.project-title').first.text, u'WOMEN FIRST')

        self.assertEqual(self.browser.find_by_css('.fund-amount-control label').first.text, u"I'D LIKE TO GIVE")
        self.assertTrue(u'495' in self.browser.find_by_css('.fund-amount-needed').first.text)
        input_field = self.browser.find_by_css('.fund-amount-control input').first
        self.assertEqual(input_field['name'], u'fund-amount-1')
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
        time.sleep(2)
        # Don't sign up. Skip this form.
        self.browser.find_link_by_partial_text('Skip').first.click()

        self.assertTrue(self.browser.is_text_present("YOU'RE ALMOST THERE!", wait_time=5))

        # Proceed with the payment

        # self.browser.find_link_by_partial_text('Proceed').first.click()
        # self.assertTrue(self.browser.is_text_present('YOUR PAYMENT'))
        # self.assertTrue(self.browser.url.find('https://test.docdatapayments.com/') != -1)
        #
        # # Select Ideal + ING for payment
        #
        # self.browser.find_by_css('div.paymentChoiceMenuRow.ideal').first.click()
        # time.sleep(2)
        # self.browser.find_by_css("div.paymentChoiceMenuRow.ideal select.flowHorizontal").first.click()
        # time.sleep(2)
        # self.browser.find_by_css("div.paymentChoiceMenuRow.ideal option[value=ING]").first.click()
        # time.sleep(1)
        # self.browser.find_link_by_text('to iDEAL').first.click()
        #
        # time.sleep(2)
        #
        # self.assertTrue(self.browser.url.find('https://test.tripledeal.com/') != -1)



        self.assertTrue(self.login(username=self.some_user.email, password='password'))

        # Create dummy donation, so we can validate the thank you page.
        donation = self.create_donation(self.some_user, self._projects[0])
        donation.order.status = OrderStatuses.current
        donation.order.closed = None

        from apps.cowry_docdata.models import DocDataPaymentOrder
        DocDataPaymentOrder.objects.create(order=donation.order, payment_order_id='dummy')

        donation.order.save()
        donation.save()

        self.visit_path('/support/thanks/{0}'.format(donation.order.pk))

        # Validate thank you page.
        self.assertTrue(self.browser.is_text_present('WELL, YOU ROCK!'))
        self.assertTrue(self.browser.is_text_present(self._projects[0].title.upper()))

        # check that the correct links are present
        self.browser.find_by_css('li.project-list-item a').first.click()
        self.assertEqual(self.browser.url, '{0}/en/#!/projects/{1}'.format(self.live_server_url, self._projects[0].slug))

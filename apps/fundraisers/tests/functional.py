import os
from django.utils import timezone

from django.utils.unittest.case import skipUnless
from django.conf import settings

from bluebottle.bluebottle_utils.tests import UserTestsMixin
from onepercentclub.tests.utils import OnePercentSeleniumTestCase

from apps.fund.models import DonationStatuses, Donation, OrderStatuses
from apps.projects.tests.unittests import ProjectTestsMixin
from apps.donations.tests.helpers import DonationTestsMixin

from ..models import FundRaiser
from .helpers import FundRaiserTestsMixin


@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
        'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class FundRaiserSeleniumTest(FundRaiserTestsMixin, ProjectTestsMixin, UserTestsMixin, DonationTestsMixin, OnePercentSeleniumTestCase):
    """
    Integration tests for the fundraiser API.
    """
    def setUp(self):
        """
        Create initial data.
        """
        self.project_with_fundraiser = self.create_project(money_asked=50000)
        self.project_without_fundraiser = self.create_project(money_asked=75000)

        self.some_user = self.create_user()
        self.another_user = self.create_user()

        self.fundraiser = self.create_fundraiser(self.some_user, self.project_with_fundraiser)

        self.project_with_fundraiser_url = '/projects/{0}'.format(self.project_with_fundraiser.slug)
        self.project_without_fundraiser_url = '/projects/{0}'.format(self.project_without_fundraiser.slug)

        self.fundraiser_url = '/fundraisers/{0}'.format(self.fundraiser.pk)
        self.new_fundraiser_url = '/project/{0}/new-fundraiser'.format(self.project_without_fundraiser.slug)

        # Force reload by visiting the home
        self.visit_path('')
        # Force refresh of the browser to work with the new database state, rather then Ember using a cached version.
        #self.browser.driver.refresh()

    def test_link_from_project_page_to_create_fundraiser_anonymous(self):
        """
        Test create a fundraiser for a project as anonymous user.
        """
        self.visit_path(self.project_with_fundraiser_url)

        self.browser.find_link_by_partial_text('Become a fundraiser').first.click()

        self.assertTrue(self.browser.is_itext_present('NEW FUNDRAISER'))
        self.assertTrue(self.browser.is_text_present('You need to be logged in to start fundraising.'))

    def test_link_from_project_page_to_create_fundraiser_authenticated(self):
        """
        Test create a fundraiser for a project as authenticated user.
        """
        self.login(username=self.some_user.email, password='password')

        self.visit_path(self.project_with_fundraiser_url)

        self.browser.find_link_by_partial_text('Become a fundraiser').first.click()

        self.assertTrue(self.browser.is_text_present('Fundraising for project'))
        self.assertFalse(self.browser.is_text_present('You need to be logged in to start fundraising.'))

        deadline = timezone.now() + timezone.timedelta(days=28)
        filepath = os.path.join(os.path.dirname(__file__), 'test_files', 'upload.png')

        self.browser.fill_form_by_label(
            self.browser.find_by_css('form#fundraiser-new').first,
            [
                ('Title', 'Run for the cause'),
                ('Description', 'I will run for joy and to help the cause.'),
                ('Image', filepath),
                ('Video', ''),
                ('Amount to raise', '1000'),
                ('Deadline', [None, deadline.strftime('%d/%m/%Y')]),
            ]
        )

        self.browser.find_by_css('button.btn.btn-iconed.btn-next').first.click()

        self.assertTrue(self.browser.is_text_present('FUNDRAISING FOR'))

        self.assertEqual(self.browser.url, '{0}/en/#!/fundraisers/2'.format(self.live_server_url))

        self.assertTrue(self.browser.is_text_present('RUN FOR THE CAUSE'))

        fundraisers = FundRaiser.objects.filter(title='Run for the cause')
        self.assertEqual(fundraisers.count(), 1)
        self.assertEqual(fundraisers[0].amount, 100000)

    def test_link_from_fundraiser_page_to_edit_fundraiser_authenticated(self):
        """
        Test edit a fundraiser that the user does not own.
        """
        self.login(username=self.another_user.email, password='password')

        self.visit_path(self.fundraiser_url)

        self.assertFalse(self.browser.is_text_present('Edit'))

        # Visit link anyway
        self.visit_path('{0}/edit'.format(self.fundraiser_url))

        self.assertTrue(self.browser.is_text_present('EDIT FUNDRAISER'))
        self.assertTrue(self.browser.is_text_present('You can only make a fundraiser if you are logged in and the owner of this fundraiser.'))
        self.assertFalse(self.browser.is_text_present('Amount to raise'))

    def test_link_from_fundraiser_page_to_edit_fundraiser_as_owner(self):
        """
        Test edit a fundraiser that the user owns.
        """
        self.login(username=self.some_user.email, password='password')

        self.visit_path(self.fundraiser_url)

        self.browser.find_link_by_partial_text('Edit').first.click()

        self.assertTrue(self.browser.is_text_present('EDIT FUNDRAISER'))
        self.assertFalse(self.browser.is_text_present('You can only make a fundraiser if you are logged in and the owner of this fundraiser.'))
        self.assertTrue(self.browser.is_text_present('Amount to raise'))

        self.assertEqual(self.browser.url, '{0}/en/#!/fundraisers/{1}/edit'.format(self.live_server_url, self.fundraiser.pk))

        deadline = timezone.now() + timezone.timedelta(days=28)
        filepath = os.path.join(os.path.dirname(__file__), 'test_files', 'upload.png')

        self.browser.fill_form_by_label(
            self.browser.find_by_css('form#fundraiser-edit').first,
            [
                ('Title', 'Run for the cause'),
                ('Description', 'I will run for joy and to help the cause.'),
                ('Image', filepath),
                ('Video', ''),
                ('Amount to raise', '1000'),
                ('Deadline', [None, deadline.strftime('%d/%m/%Y')]),
            ]
        )

        # Press save
        self.browser.find_by_css('button.btn.btn-iconed.btn-next').first.click()

        # Validate transition to fundraiser page
        self.assertTrue(self.browser.is_text_present('RUN FOR THE CAUSE'))
        self.assertEqual(self.browser.url, '{0}/en/#!/fundraisers/{1}'.format(self.live_server_url, self.fundraiser.pk))

        # Reload fundraiser
        fundraiser = FundRaiser.objects.get(pk=self.fundraiser.pk)

        # Validate updated properties
        self.assertEqual(fundraiser.amount, 100000)
        self.assertEqual(fundraiser.title, 'Run for the cause')
        self.assertEqual(fundraiser.description, 'I will run for joy and to help the cause.')

    def test_link_from_project_to_fundraiser_page(self):
        """
        Test navigate from project to fundraise page.
        """
        self.visit_path(self.project_with_fundraiser_url)

        self.browser.find_link_by_href('#!{0}'.format(self.fundraiser_url)).first.click()

        self.assertEqual(self.browser.url, '{0}/en/#!{1}'.format(self.live_server_url, self.fundraiser_url))

        self.assertTrue(self.fundraiser.title != '')
        self.assertTrue(self.browser.is_text_present(self.fundraiser.title.upper()))

    def test_fundraise_page(self):
        """
        Test information on fundraise page.
        """
        self.visit_path(self.fundraiser_url)

        self.assertTrue(self.fundraiser.title != '')
        self.assertTrue(self.browser.is_text_present(self.fundraiser.title.upper()))

        link = self.browser.find_link_by_partial_text(self.project_with_fundraiser.title)

        # TODO: check link

    def test_fundraise_donation(self):
        """
        Test create donation for fundraise action.
        """
        self.login(username=self.some_user.email, password='password')

        self.visit_path(self.fundraiser_url)

        self.assertTrue(self.fundraiser.title != '')
        self.assertTrue(self.browser.is_text_present(self.fundraiser.title.upper()))

        # Go to donate page.
        # TODO: This fails for some reason, we use an alternative method:
        #self.browser.find_link_by_partial_text('Support').first.click()
        self.browser.find_by_css('a.btn.btn-primary.btn-iconed').first.click()

        # Validate donation page.
        self.assertTrue(self.browser.is_text_present('SUPPORT'))
        self.assertTrue(self.browser.is_text_present(self.fundraiser.title.upper()))
        self.assertTrue(self.browser.is_text_present('TOTAL'))

        self.assertEqual(self.browser.url, '{0}/en/#!/support/donations'.format(self.live_server_url))

        self.browser.find_by_css('button.btn.btn-iconed.btn-next').first.click()

        # Validate personal info page.
        self.assertTrue(self.browser.is_text_present('SUPPORT'))
        self.assertTrue(self.browser.is_text_present('Please verify your details.'))

        self.assertEqual(self.browser.url, '{0}/en/#!/support/details'.format(self.live_server_url))

        # TODO: Test rest of the flow?

        # Create dummy donation, so we can validate the thank you page.
        donation = self.create_donation(self.some_user, self.project_with_fundraiser)
        donation.fundraiser = self.fundraiser
        donation.order.status = OrderStatuses.current
        donation.order.closed = None

        from apps.cowry_docdata.models import DocDataPaymentOrder
        DocDataPaymentOrder.objects.create(order=donation.order, payment_order_id='dummy')

        donation.order.save()
        donation.save()

        self.visit_path('/support/thanks/{0}'.format(donation.order.pk))

        # Validate thank you page.
        self.assertTrue(self.browser.is_text_present('WELL, YOU ROCK!'))
        self.assertTrue(self.browser.is_text_present(self.fundraiser.title.upper()))

        # check that the correct links are present
        self.browser.find_by_css('li.project-list-item a').first.click()
        self.assertEqual(self.browser.url, '{0}/en/#!/fundraisers/{1}'.format(self.live_server_url, self.fundraiser.id))

import json

from django.core.urlresolvers import reverse

from rest_framework import status

from bluebottle.bluebottle_utils.tests import UserTestsMixin
from onepercentclub.tests.utils import OnePercentSeleniumTestCase

from apps.fund.models import DonationStatuses, Donation
from apps.projects.tests.unittests import ProjectTestsMixin

from ..models import FundRaiser
from .helpers import FundRaiserTestsMixin


class FundRaiserSeleniumTest(FundRaiserTestsMixin, ProjectTestsMixin, UserTestsMixin, OnePercentSeleniumTestCase):
    """
    Integration tests for the fundraiser API.
    """

    def setUp(self):
        """ Create two project instances """
        self.project_with_fundraiser = self.create_project(money_asked=50000)
        self.project_without_fundraiser = self.create_project(money_asked=75000)

        self.some_user = self.create_user()
        self.another_user = self.create_user()

        self.fundraiser = self.create_fundraiser(self.some_user, self.project_with_fundraiser)

        self.project_with_fundraiser_url = '/projects/{0}'.format(self.project_with_fundraiser.slug)
        self.project_without_fundraiser_url = '/projects/{0}'.format(self.project_without_fundraiser.slug)

        self.fundraiser_url = '/fundraiser/{0}'.format(self.fundraiser.pk)
        self.new_fundraiser_url = '/my/fundraiser/new/{0}'.format(self.project_without_fundraiser.slug)

    def test_link_from_project_page_to_create_fundraiser(self):
        self.visit_path(self.project_with_fundraiser_url)

        self.browser.find_link_by_text('Become a fundraiser').first.click()

        self.assertTrue(self.browser.is_text_present('NEW FUNDRAISER'))

    def test_link_from_project_to_fundraiser_page(self):
        self.visit_path(self.project_with_fundraiser_url)

        #self.browser.find_link_by_text('Become a fundraiser').first.click()

        #self.assertTrue(self.browser.is_text_present('NEW FUNDRAISER'))

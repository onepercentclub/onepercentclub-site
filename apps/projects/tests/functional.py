# -*- coding: utf-8 -*-
"""
Functional tests using Selenium.

See: ``docs/testing/selenium.rst`` for details.
"""
import time

from django.conf import settings
from django.utils.text import slugify
from django.utils.unittest.case import skipUnless

from ..models import Project, ProjectPhases
from .unittests import ProjectTestsMixin

from bluebottle.tests.utils import SeleniumTestCase


@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
        'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class ProjectSeleniumTests(ProjectTestsMixin, SeleniumTestCase):
    """
    Selenium tests for Projects.
    """
    def setUp(self):
        self.projects = dict([(slugify(title), title) for title in [
            u'Women first 2', u'Mobile payments for everyone 2!', u'Schools for children 2'
        ]])

        for slug, title in self.projects.items():
            project = self.create_project(title=title, slug=slug, money_asked=100000)
            project.projectcampaign.money_donated = 0
            project.projectcampaign.save()

    def visit_project_list_page(self, lang_code=None):
        self.visit_path('/projects', lang_code)

        self.assertTrue(self.browser.is_element_present_by_css('.item.item-project'),
                'Cannot load the project list page.')

    def test_navigate_to_project_list_page(self):
        """
        Test navigate to the project list page.
        """
        self.visit_homepage()

        # Find the link to the Projects page and click it.
        self.browser.find_link_by_text('1%Projects').first.click()

        # Validate that we are on the intended page.
        self.assertTrue(self.browser.is_element_present_by_css('.item.item-project'),
                'Cannot load the project list page.')

        self.assertEqual(self.browser.url, '%s/en/#!/projects' % self.live_server_url)
        self.assertEqual(self.browser.title, '1%Club - Share a little. Change the world')

    def test_view_project_list_page(self):
        """
        Test view the project list page correctly.
        """
        self.visit_project_list_page()

        # Besides the waiting for JS to kick in, we also need to wait for the funds raised animation to finish.
        time.sleep(2)

        def convert_money_to_int(money_text):
            return int(money_text.strip(u'€ ').replace('.', '').replace(',', ''))

        # NOTE: Due to a recent change, its harder to calculate/get the financiel data from the front end.
        # Hence, these calculations are commented. Perhaps enable in the future if this data becomes available again.

        # Create a dict of all projects on the web page.
        web_projects = []
        for p in self.browser.find_by_css('.item.item-project'):
            # NOTE: donated class name should be read as "to go"...
            donated = convert_money_to_int(p.find_by_css('.donated').first.text)
            #asked = convert_money_to_int(p.find_by_css('.asked').first.text)

            web_projects.append({
                'title': p.find_by_css('h3').first.text,
                'money_needed': donated,
                #'money_asked': asked,
            })

            # Validate the donation slider.
            # NOTE: It's an animation. We expect it to be done after a few seconds.
            #expected_slider_value = ((Decimal('100') / asked) * donated)
            #web_slider_value = Decimal(css_dict(p.find_by_css('.donate-progress').first['style'])['width'].strip('%'))

            # We allow a small delta to deviate.
            #self.assertAlmostEqual(web_slider_value, expected_slider_value, delta=1)

        # Make sure there are some projects to compare.
        self.assertTrue(len(web_projects) > 0)

        # Create dict of projects in the database.
        expected_projects = []
        for p in Project.objects.filter(phase=ProjectPhases.campaign).order_by('popularity')[:len(web_projects)]:
            expected_projects.append({
                'title': p.title.upper(),  # Uppercase the title for comparison.
                'money_needed': int(round(p.projectcampaign.money_needed / 100.0)),
                #'money_asked': int(round(p.projectcampaign.money_asked / 100.0))
            })

        # Compare all projects found on the web page with those in the database, in the same order.
        self.assertListEqual(web_projects, expected_projects)

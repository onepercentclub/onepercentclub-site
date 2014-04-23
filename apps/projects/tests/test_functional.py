# -*- coding: utf-8 -*-
"""
Functional tests using Selenium.

See: ``docs/testing/selenium.rst`` for details.
"""
from bluebottle.test.factory_models.utils import LanguageFactory
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils.unittest.case import skipUnless


from bluebottle.geo import models as geo_models
from onepercentclub.tests.utils import OnePercentSeleniumTestCase

from onepercentclub.tests.utils import OnePercentSeleniumTestCase
from bluebottle.test.factory_models.accounts import BlueBottleUserFactory
from bluebottle.test.factory_models.projects import ProjectThemeFactory, ProjectPhaseFactory
from onepercentclub.tests.factory_models.project_factories import OnePercentProjectFactory

from ..models import Project, ProjectTheme

import os
import time


@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
        'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class ProjectSeleniumTests(OnePercentSeleniumTestCase):
    """
    Selenium tests for Projects.
    """
    def setUp(self):
        self.phase_1 = ProjectPhaseFactory.create(sequence=1, name='Plan - New')
        self.phase_2 = ProjectPhaseFactory.create(sequence=2, name='Campaign')

        self.projects = dict([(slugify(title), title) for title in [
           u'Mobile payments for everyone 2!', u'Schools for children 2',  u'Women first 2'
        ]])

        self.user = BlueBottleUserFactory.create(email='johndoe@example.com', primary_language='en')

        for slug, title in self.projects.items():
            project = OnePercentProjectFactory.create(title=title, slug=slug, owner=self.user, amount_asked=1000)

    def visit_project_list_page(self, lang_code=None):
        self.visit_path('/projects', lang_code)

        self.assertTrue(self.browser.is_element_present_by_css('.project-item'),
                'Cannot load the project list page.')

    def test_navigate_to_project_list_page(self):
        """
        Test navigate to the project list page.
        """
        self.visit_homepage()

        # Find the link to the Projects page and click it.
        self.browser.find_link_by_text('1%Projects').first.click()

        # Validate that we are on the intended page.
        self.assertTrue(self.browser.is_element_present_by_css('.project-item'),
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
            amount = money_text.strip(' TO GO').strip(u'€').strip(u'\u20ac').replace('.', '').replace(',', '')
            if not amount:
                amount = 0
            return int(amount)

        # NOTE: Due to a recent change, its harder to calculate/get the financiel data from the front end.
        # Hence, these calculations are commented. Perhaps enable in the future if this data becomes available again.

        # Create a dict of all projects on the web page.
        web_projects = []
        for p in self.browser.find_by_css('#search-results .project-item'):
            title = p.find_by_css('h3').first.text
            needed = convert_money_to_int(p.find_by_css('.project-fund-amount').first.text)
            web_projects.append({
                'title': title,
                'amount_needed': needed,
            })

        # Make sure there are some projects to compare.
        self.assertTrue(len(web_projects) > 0)

        # Create dict of projects in the database.
        expected_projects = []
        for p in Project.objects.order_by('popularity')[:len(web_projects)]:
            expected_projects.append({
                'title': p.title.upper(),  # Uppercase the title for comparison.
                'amount_needed': int(round(p.amount_needed / 100.0)),
            })

        # Compare all projects found on the web page with those in the database, in the same order.
        self.assertListEqual(web_projects, expected_projects)

    @skipUnless(getattr(settings, 'SELENIUM_WEBDRIVER') == 'firefox',
        'PhantomJS keeps hanging on the file uploads, probably bug in selenium/phantomjs')
    def test_upload_multiple_wallpost_images(self):
        """ Test uploading multiple images in a media wallpost """

        self.login(self.user.email, 'testing')
        self.visit_project_list_page()

        # pick a project
        self.browser.find_by_css('.project-item').first.find_by_tag('a').first.click()

        form = self.browser.find_by_id('wallpost-form')

        self.browser.find_by_id('wallpost-title').first.fill('My wallpost')
        self.browser.find_by_id('wallpost-update').first.fill('These are some sample pictures from this non-existent project!')

        # verify that no previews are there yet
        ul = form.find_by_css('ul.form-wallpost-photos').first
        previews = ul.find_by_tag('li')
        self.assertEqual(0, len(previews))

        # attach file
        file_path = os.path.join(settings.PROJECT_ROOT, 'static', 'tests', 'kitten_snow.jpg')
        self.browser.attach_file('wallpost-photo', file_path)

        # verify that one picture was added
        form = self.browser.find_by_id('wallpost-form')
        ul = form.find_by_css('ul.form-wallpost-photos').first
        previews = ul.find_by_tag('li')

        # verify that a second picture was added
        file_path = os.path.join(settings.PROJECT_ROOT, 'static', 'tests', 'chameleon.jpg')
        self.browser.attach_file('wallpost-photo', file_path)

        # wait a bit, processing...
        time.sleep(3)

        form = self.browser.find_by_id('wallpost-form')
        ul = form.find_by_css('ul.form-wallpost-photos').first
        previews = ul.find_by_tag('li')
        self.assertEqual(2, len(previews))

        # submit the form
        form.find_by_tag('button').first.click();

        # check if the wallpostis there
        wp = self.browser.find_by_css('article.wallpost').first
        self.assertTrue(self.browser.is_text_present('MY WALLPOST'))

        num_photos = len(wp.find_by_css('ul.photo-viewer li.photo'))
        self.assertEqual(num_photos, 2)


    def test_meta_tag(self, lang_code=None):
        self.visit_path('/projects/schools-for-children-2', lang_code)

        time.sleep(2)
        self.assertIn('Schools for children 2', self.browser.title) # check that the title indeed contains the project title

        # check meta url
        meta_url = self.browser.find_by_xpath("//html/head/meta[@property='og:url']").first
        self.assertEqual(self.browser.url, meta_url['content'])

        # TODO: check that the default description is overwritten, add description to plan



@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
            'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class ProjectCreateSeleniumTests(OnePercentSeleniumTestCase):
    """
    Selenium tests for Projects.
    """
    fixtures = ['booking_project_phases.json']

    def setUp(self):
        self.user = BlueBottleUserFactory.create()
        self.theme1 = ProjectThemeFactory.create()
        self.theme2 = ProjectThemeFactory.create()

        self.language1 = LanguageFactory.create()
        self.language2 = LanguageFactory.create()

        self.login(self.user.email, 'testing')

        self.project_data = {
            'title': 'Velit esse cillum dolore',
            'slug': 'velit-esse-cillum-dolore',
            'pitch': 'Quis aute iure reprehenderit in voluptate eu fugiat nulla pariatur.',
            'tags': ['okoali', 'kertan', 'lorem'],
            'description': 'Stet clita kasd gubergren.\nNo sea takimata sanctus est Lorem ipsum dolor sit amet. Sanctus sea sed takimata ut vero voluptua.\n\nStet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Sanctus sea sed takimata ut vero voluptua. Excepteur sint obcaecat cupiditat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
            'goal': 'Lorem ipsum dolor sit amet. Sanctus sea sed takimata ut vero voluptua. Excepteur sint obcaecat cupiditat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
            'destination_impact': 'Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.',
            'amount_asked': 5000,
            'budget': [
                {'description': 'Ghaks', 'amount': 4000},
                {'description': 'Rausno', 'amount': 500},
                {'description': 'Jama Jurnoader', 'amount': 500}
                ]
            }

    def test_create_project(self):
        """
        Test to load the first page for creating a project.
        """

        self.visit_path('/my/projects')
        self.assertTrue(self.browser.is_text_present('CREATE NEW PROJECT', wait_time=15))


        # Click "Pitch Smart Idea" btn
        self.browser.find_by_id("create_project").first.click()

        self.assertTrue(self.browser.is_text_present('PROJECT START', wait_time=5))

        self.assertEqual(self.browser.url, '{0}/en/#!/my/projects/new/start'.format(self.live_server_url))


        time.sleep(3)
        self.browser.find_by_css(".btn-primary").first.click()

        time.sleep(2)

        # self.assertTrue(self.browser.is_text_present('Title', wait_time=5))

        self.browser.select('language', 2)
        self.browser.fill('title', self.project_data['title'])
        self.browser.fill('pitch', self.project_data['pitch'])

        btn = self.browser.attach_file('img_upload', '{0}/apps/projects/test_images/upload.png'.format(settings.PROJECT_ROOT))

        time.sleep(2)

        # Splinter takes the value of the select option
        self.browser.select('theme', 2)

        for tag in self.project_data['tags']:
            self.browser.fill('tag', tag)
            self.browser.find_by_css("button.add-tag").first.click()

        #self.browser.select('country', 1)

        self.browser.find_by_css('button.next').first.click()

        self.assertTrue(self.browser.is_text_present('GOAL', wait_time=5))

        # Goal & Budget

        self.browser.fill('amount_asked', self.project_data['amount_asked'])

        # Pick a deadline next month
        self.assertTrue(self.scroll_to_and_click_by_css(".btn-date-picker"))

        # Wait for date picker popup
        self.assertTrue(self.browser.is_element_present_by_css("#ui-datepicker-div"))

        # Click Next to get a date in the future
        self.browser.find_by_css("[title=Next]").first.click()
        self.assertTrue(self.browser.is_text_present("10"))
        self.browser.find_link_by_text("10").first.click()


        for line in self.project_data['budget']:
            self.browser.fill('budget_line_amount', line['amount'])
            self.browser.fill('budget_line_description', line['description'])
            time.sleep(1)
            self.browser.find_by_css("a.add-budget").first.click()


        self.browser.find_by_css("button.next").first.click()

        self.assertTrue(self.browser.is_text_present('PROJECT DESCRIPTION', wait_time=50))
        self.assertEqual(self.browser.url,
                         '{0}/en/#!/my/projects/{1}/story'.format(self.live_server_url,
                                                                  self.project_data['slug']))

        story = self.browser.find_by_css('.redactor_redactor').first
        story.type(self.project_data['description'])

        self.browser.find_by_css("button.next").first.click()

        self.assertTrue(self.browser.is_text_present('ORGANISATION', wait_time=5))

        self.assertEqual(self.browser.url, '{0}/en/#!/my/projects/{1}/organisation'.format(self.live_server_url,
                                                                                           self.project_data['slug']))
        organisation = {
            "name": "Test Organization",
            "email": "harold@testorg.com",
            "phone": "123456789",
            "website": "http://www.testorg.com",
            "twitter": "@testorg",
            "facebook": "testorg",
            "skype": "testorg"
        }

        self.browser.fill('name', organisation['name'])
        self.browser.fill('email', organisation['email'])
        self.browser.fill('phone', organisation['phone'])
        self.browser.fill('website', organisation['website'])
        self.browser.fill('twitter', organisation['twitter'])
        self.browser.fill('facebook', organisation['facebook'])
        self.browser.fill('skype', organisation['skype'])

        self.browser.find_by_css("button.next").first.click()

        self.assertTrue(self.browser.is_text_present('Please fill in all information before submitting', wait_time=5))
        self.assertEqual(self.browser.url,
                         '{0}/en/#!/my/projects/{1}/submit'.format(self.live_server_url,
                                                                   self.project_data['slug']))

        # confirm the project record was created
        # TODO: Also check it has the expected fields.
        Project.objects.filter(slug=self.project_data['slug']).exists()


@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
            'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class ProjectWallPostSeleniumTests(OnePercentSeleniumTestCase):
    """
    Selenium tests for Projects.
    """
    def setUp(self):
        self.user = BlueBottleUserFactory.create()
        self.login(self.user.email, 'testing')

        self.project = OnePercentProjectFactory.create()
        self.project.owner = BlueBottleUserFactory.create()
        self.project.save()

        self.post1 = {
            'text': 'Ziltch emit doler omit et dametis!'
        }
        self.post2 = {
            'title': 'Hora est',
            'text': 'Rolum dohar in amuet redicer...'
        }

    def test_write_wall_post(self):
        """
        Test to write wall-posts on project page
        """
        self.visit_path('/projects/{0}'.format(self.project.slug))
        self.assertTrue(self.browser.is_text_present(self.project.title, wait_time=5))
        self.assertTrue(self.browser.is_text_present('Post a new comment on wall', wait_time=5))

        self.browser.find_by_css(".wallpost-post-update").click()
        self.assertTrue(self.browser.is_text_present('Post', wait_time=5))

        # Write wallpost as normal user
        self.browser.fill('wallpost-update', self.post1['text'])
        self.browser.find_by_css("button.btn-save").first.click()

        post = self.browser.find_by_css("article.wallpost").first

        self.assertEqual(post.find_by_css('.wallpost-author').text, self.user.short_name)
        self.assertEqual(post.find_by_css('.text p').text, self.post1['text'])

        self.logout()

        # Login as the project owner
        self.login(self.project.owner.email, 'testing')

        # Should see the post by the first user.
        self.visit_path('/projects/{0}'.format(self.project.slug))
        post = self.browser.find_by_css("article.wallpost").first
        self.assertEqual(post.find_by_css('.wallpost-author').text, self.user.short_name)
        self.assertEqual(post.find_by_css('.text p').text, self.post1['text'])

        # Post as project owner
        self.browser.find_by_css(".wallpost-post-update").click()
        self.assertTrue(self.browser.is_text_present('Post', wait_time=5))

        self.browser.fill('wallpost-title', self.post2['title'])
        self.browser.fill('wallpost-update', self.post2['text'])
        self.browser.find_by_css("button.btn-save").first.click()

        # Check that the new wallpost is there
        self.assertTrue(self.browser.is_text_present('INITIATOR', wait_time=5))
        # Wait for title, so we're sure the animation is finished.
        self.assertTrue(self.browser.is_text_present(self.post2['title'], wait_time=5))
        post = self.browser.find_by_css("article.wallpost")[0]

        self.assertEqual(post.find_by_css('.wallpost-author').text, self.project.owner.short_name)
        self.assertEqual(post.find_by_css('.wallpost-title').text, self.post2['title'])
        self.assertEqual(post.find_by_css('.text p').text, self.post2['text'])

        # And the first post should still be shown as second
        post = self.browser.find_by_css("article.wallpost")[1]
        self.assertEqual(post.find_by_css('.wallpost-author').text, self.user.short_name)
        self.assertEqual(post.find_by_css('.text p').text, self.post1['text'])


# -*- coding: utf-8 -*-
"""
Functional tests using Selenium.

See: ``docs/testing/selenium.rst`` for details.
"""
from decimal import Decimal
from bluebottle.bb_projects.models import ProjectPhase
from bluebottle.utils.models import Language
from django.conf import settings
from django.utils.text import slugify
from django.utils.unittest.case import skipUnless

from onepercentclub.tests.utils import OnePercentSeleniumTestCase
from onepercentclub.tests.factory_models.project_factories import OnePercentProjectFactory

from bluebottle.test.factory_models.accounts import BlueBottleUserFactory
from bluebottle.test.factory_models.geo import CountryFactory


from ..models import Project

import os
import time


@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
        'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class ProjectSeleniumTests(OnePercentSeleniumTestCase):
    """
    Selenium tests for Projects.
    """
    def setUp(self):
        self.init_projects()

        self.projects = dict([(slugify(title), title) for title in [
           u'Mobile payments for everyone 2!', u'Schools for children 2',  u'Women first 2'
        ]])

        self.user = BlueBottleUserFactory.create(email='johndoe@example.com', primary_language='en')

        campaign_phase = ProjectPhase.objects.get(slug='campaign')

        for slug, title in self.projects.items():
            project = OnePercentProjectFactory.create(title=title, slug=slug, owner=self.user,
                                                      amount_asked=1000, status=campaign_phase)

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

        time.sleep(10)
        # Validate that we are on the intended page.
        self.assertTrue(self.browser.is_element_present_by_css('.project-item'), 'Cannot load the project list page.')

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
            amount = money_text.strip(u'€').strip(u'\u20ac').replace('.', '').replace(',', '')
            if not amount:
                amount = 0
            return amount
            #return int(amount)

        # NOTE: Due to a recent change, its harder to calculate/get the financiel data from the front end.
        # Hence, these calculations are commented. Perhaps enable in the future if this data becomes available again.

        # Create a dict of all projects on the web page.
        web_projects = []
        for p in self.browser.find_by_css('#search-results .project-item'):
            title = p.find_by_css('h3').first.text
            needed = convert_money_to_int(p.find_by_css('.project-fund-amount strong').first.text)
            web_projects.append({
                'title': title,
            #    'amount_donated': needed,
            })

        # Make sure there are some projects to compare.
        self.assertTrue(len(web_projects) > 0)

        # Create dict of projects in the database.
        expected_projects = []
        for p in Project.objects.order_by('popularity')[:len(web_projects)]:
            expected_projects.append({
                'title': p.title.upper(),  # Uppercase the title for comparison.
            #    'amount_donated': int(round(p.amount_donated / Decimal(100.0))),
            })

        # Compare all projects found on the web page with those in the database, in the same order.

        # FIXME: Fix me! Please fix me!
        # This isn't working because popularity & donations isn't.
        # self.assertListEqual(web_projects, expected_projects)

    def test_upload_multiple_wallpost_images(self):
        """ Test uploading multiple images in a media wallpost """

        self.assertTrue(self.login(self.user.email, 'testing'))
        self.visit_project_list_page()

        # pick a project
        self.browser.find_by_css('.project-item').first.find_by_tag('a').first.click()

        form = self.browser.find_by_id('wallpost-form')

        self.browser.find_by_css('.wallpost-post-update').first.click()

        # Wait for form to animate down
        self.wait_for_element_css('#wallpost-title')

        title = 'My wallpost'
        self.browser.find_by_id('wallpost-title').first.fill(title)
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

        # Wait for the second item to be added
        self.wait_for_element_css('ul.form-wallpost-photos li:nth-child(2)')

        form = self.browser.find_by_id('wallpost-form')
        ul = form.find_by_css('ul.form-wallpost-photos').first
        previews = ul.find_by_tag('li')
        self.assertEqual(2, len(previews))

        # submit the form
        form.find_by_tag('button').first.click();

        # check if the wallpostis there
        wp = self.browser.find_by_css('article.wallpost').first

        self.assertTrue(self.browser.is_text_present(title))

        num_photos = len(wp.find_by_css('ul.photo-viewer li.photo'))
        self.assertEqual(num_photos, 2)


    def test_meta_tag(self, lang_code=None):
        self.visit_path('/projects/schools-for-children-2', lang_code)

        time.sleep(4)
        #self.assertIn('Schools for children 2', self.browser.title) # check that the title indeed contains the project title

        # check meta url
        meta_url = self.browser.find_by_xpath("//html/head/meta[@property='og:url']").first
        self.assertEqual(self.browser.url, meta_url['content'])

        # TODO: check that the default description is overwritten, add description to plan

    def test_project_plan(self):
        self.visit_path('/projects/schools-for-children-2')

        element = self.wait_for_element_css('.project-plan-link a')
        element.click()

        self.wait_for_element_css('.project-plan-navigation-links')
        self.assertTrue(self.browser.is_element_not_present_by_css('.project-plan-download-pdf'), 'PDF download should not be available')


@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
            'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class ProjectCreateSeleniumTests(OnePercentSeleniumTestCase):
    """
    Selenium tests for Projects.
    """

    def setUp(self):

        self.init_projects()
        self.user = BlueBottleUserFactory.create()

        self.country_1 = CountryFactory.create(name="Afghanistan")
        self.country_2 = CountryFactory.create(name="Albania")

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
        Creating a project. The positive flow.
        """

        self.visit_path('/my/projects')

        # Click "Pitch Smart Idea" btn
        self.assertTrue(self.is_visible('#create_project'))
        self.browser.find_by_id("create_project").first.click()

        ###
        # Intro Section
        ###

        self.assertTrue(self.is_visible('section h1.page-title'))
        self.scroll_to_and_click_by_css("button.btn-primary")

        ###
        # Project Section
        ###

        self.browser.select('language', 2)
        self.browser.fill('title', self.project_data['title'])
        self.browser.fill('pitch', self.project_data['pitch'])

        btn = self.browser.attach_file('img_upload', '{0}/apps/projects/test_images/upload.png'.format(settings.PROJECT_ROOT))

        # Splinter takes the value of the select option
        self.browser.select('theme', 2)

        for tag in self.project_data['tags']:
            self.browser.fill('tag', tag)
            self.browser.find_by_css("button.add-tag").first.click()

        self.browser.select('country', 1)

        self.scroll_to_and_click_by_css("button.next")

        ###
        # Goal Section
        ###

        self.assertTrue(self.is_visible('input[name="amount_asked"]'))

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

        self.scroll_to_and_click_by_css("button.next")

        ###
        # Description Section
        ###

        self.assertTrue(self.is_visible('.redactor_editor'))

        self.assertEqual(self.browser.url,
                         '{0}/en/#!/my/projects/{1}/story'.format(self.live_server_url,
                                                                  self.project_data['slug']))

        story = self.browser.find_by_css('.redactor_redactor').first
        story.type(self.project_data['description'])

        self.scroll_to_and_click_by_css("button.next")

        ###
        # Organisation Section
        ###

        self.wait_for_element_css('input[name="name"]')

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

        btn = self.browser.attach_file('documents', '{0}/apps/projects/test_images/upload.png'.format(settings.PROJECT_ROOT))
 
        self.scroll_to_and_click_by_css("button.next")

        ###
        # Bank Section
        ###

        bank_details = {
            "name": "Test Organization",
            "address": "144 Tolstraat",
            "postcode": "1074 VM",
            "city": "Amsterdam",
            "iban": "NL91ABNA0417164300",
            "bic": "ABNANL2AXXX"
        }

        self.assertTrue(self.is_visible('input[name="account-holder-name"]'))

        self.browser.fill('account-holder-name', bank_details['name'])
        self.browser.fill('account-holder-address', bank_details['address'])
        self.browser.fill('account-holder-postcode', bank_details['postcode'])
        self.browser.fill('account-holder-city', bank_details['city'])

        self.scroll_to_and_click_by_css('select[name="account-holder-country"]')
        self.browser.select('account-holder-country', 1)

        self.scroll_to_and_click_by_css('ul.tab-control .tab-first a')
        
        self.browser.fill('account-iban', bank_details['iban'])
        self.browser.fill('account-bic', bank_details['bic'])

        self.scroll_to_and_click_by_css("button.next")

        ###
        # Submit Section
        ###

        # TODO: Add a test here to confirm that a valid project was completed by the user
        #       .... then create a new test for an invalid one.
        
        # confirm the project record was created
        # TODO: Also check it has the expected fields.
        Project.objects.filter(slug=self.project_data['slug']).exists()

    def test_change_project_goal(self):
        plan_phase = ProjectPhase.objects.get(slug='plan-new')
        project = OnePercentProjectFactory.create(title='Project Goal Changes', owner=self.user, status=plan_phase)
        self.visit_path('/my/projects/{0}/goal'.format(project.slug))

        # Check that deadline is set to 30 days now
        days_left = self.browser.find_by_css('.project-days-left strong').first
        self.assertEqual(days_left.text, '30')

        # Let's pick a date
        # Click Next to get a date in the future
        self.assertTrue(self.scroll_to_and_click_by_css(".btn-date-picker"))
        self.browser.find_by_css("[title=Prev]").first.click()
        self.browser.find_by_css("[title=Prev]").first.click()
        self.browser.find_by_css("[title=Prev]").first.click()
        self.browser.find_by_css("[title=Next]").first.click()
        self.assertTrue(self.browser.is_text_present("4"))
        self.browser.find_link_by_text("4").first.click()
        # remember the days left now
        days_left1 = self.browser.find_by_css('.project-days-left strong').first.text

        time.sleep(2)

        self.assertTrue(self.scroll_to_and_click_by_css(".btn-date-picker"))
        self.assertTrue(self.browser.is_text_present("14"))
        self.browser.find_link_by_text("14").first.click()
        days_left2 = self.browser.find_by_css('.project-days-left strong').first.text
        days_diff = int(days_left2) - int(days_left1)

        self.assertEqual(days_diff, 10)




@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
            'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class ProjectWallPostSeleniumTests(OnePercentSeleniumTestCase):
    """
    Selenium tests for Projects.
    """
    def setUp(self):
        self.init_projects()

        super(ProjectWallPostSeleniumTests, self).setUp()
        self.user = BlueBottleUserFactory.create()
        self.login(self.user.email, 'testing')

        owner = BlueBottleUserFactory.create()

        self.project = OnePercentProjectFactory.create(owner=owner)
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
        #self.assertTrue(self.browser.is_text_present(self.project.title, wait_time=5))
        self.assertTrue(self.browser.is_text_present('Post a new comment', wait_time=5))

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


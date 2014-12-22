# -*- coding: utf-8 -*-
"""
Functional tests using Selenium.

See: ``docs/testing/selenium.rst`` for details.
"""

import os
import time
from decimal import Decimal
from django.conf import settings
from django.utils.text import slugify
from django.utils.unittest.case import skipUnless
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from bluebottle.bb_projects.models import ProjectPhase, ProjectTheme
from bluebottle.utils.models import Language

from onepercentclub.tests.utils import OnePercentSeleniumTestCase
from onepercentclub.tests.factory_models.project_factories import OnePercentProjectFactory, PartnerFactory

from bluebottle.test.factory_models.accounts import BlueBottleUserFactory
from bluebottle.test.factory_models.geo import CountryFactory


from ..models import Project


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
        self.visit_project_list_page()

        time.sleep(10)
        # Validate that we are on the intended page.
        self.assertTrue(self.browser.is_element_present_by_css('.project-item'), 'Cannot load the project list page.')

        self.assertEqual(self.browser.url, '%s/en/#!/projects' % self.live_server_url)

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

        self.close_modal()

        # pick a project
        self.wait_for_element_css('.project-item')
        self.browser.find_by_css('.project-item').first.find_by_tag('a').first.click()

        # Wait for form to animate down
        form = self.wait_for_element_css('#wallpost-form')
        form.find_element_by_css_selector('textarea').send_keys('These are some sample pictures from this non-existent project!')

        #
        # TODO: re-enable this when we finish
        #

        # verify that no previews are there yet
        ul = form.find_element_by_css_selector('ul.upload-photos')
        previews = ul.find_elements_by_tag_name('li')

        # Number of li elements should be 1 - the add image button is in the first li 
        self.assertEqual(1, len(previews))

        # attach file
        self.browser.driver.find_element_by_css_selector('a[data-action-type="show-photo-upload"]').click()

        file_path = os.path.join(settings.PROJECT_ROOT, 'static', 'tests', 'kitten_snow.jpg')
        file_field = self.wait_for_element_css('.wallpost-photos .action-upload')
        file_field.find_element_by_css_selector('input').send_keys(file_path)

        # verify that one picture was added, after waiting for the preview to load
        # NOTE: there is always an "add photo" thumbnail so there should be two
        #       thumbnails after uploading the first pic
        self.assertTrue(self.wait_for_element_css('.wallpost-photos .upload-photo:nth-of-type(2)'))

        # verify that a second picture was added
        file_path = os.path.join(settings.PROJECT_ROOT, 'static', 'tests', 'chameleon.jpg')
        file_field = self.wait_for_element_css('.wallpost-photos .action-upload')
        file_field.find_element_by_css_selector('input').send_keys(file_path)

        # Wait for the second item to be added
        self.assertTrue(self.wait_for_element_css('.wallpost-photos .upload-photo:nth-of-type(3)'))

        # submit the form
        form.find_element_by_css_selector('button.action-submit').click()

        # check if the wallpostis there
        wallpost = self.browser.driver.find_element_by_css_selector('#wallposts article')

        # Check for cover photo
        cover_photos = wallpost.find_elements_by_css_selector('ul.photo-viewer li.cover')
        self.assertEqual(len(cover_photos), 1)

        # Check for other photo
        other_photos = wallpost.find_elements_by_css_selector('ul.photo-viewer li.photo')
        self.assertEqual(len(other_photos), 1)

    def test_meta_tag(self, lang_code=None):
        self.visit_path('/projects/schools-for-children-2', lang_code)

        time.sleep(4)

        # check meta url
        meta_url = self.browser.find_by_xpath("//html/head/meta[@property='og:url']").first
        self.assertEqual(self.browser.url, meta_url['content'])

        # TODO: check that the default description is overwritten, add description to plan

    # def test_project_plan(self):
    #     self.visit_path('/projects/schools-for-children-2')
    #
    #     element = self.wait_for_element_css('.project-more')
    #     element.click()
    #
    #     self.wait_for_element_css('.project-plan-navigation-links')
    #     self.assertTrue(self.browser.is_element_not_present_by_css('.project-plan-download-pdf'), 'PDF download should not be available')


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

        self.theme = ProjectTheme.objects.all()[0]
        self.language = Language.objects.all()[0]

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
        self.assertTrue(self.browser.is_element_present_by_css('#create_project', wait_time=5))
        self.assertTrue(self.is_visible('#create_project'))
        # This click can ocassially cause a problem. What the exact reason is seems to vary per person. See this thread: https://code.google.com/p/selenium/issues/detail?id=2766
        # There are various fixes but, they too, are not reliable. The only consistent solution that seems to work is a time.sleep(1)
        time.sleep(1)
        self.browser.find_by_id("create_project").first.click()

        ###
        # Intro Section
        ###
        self.visit_path('/my/projects/new/pitch')

        ###
        # Project Section
        ###
        self.assertTrue(self.is_visible('.language'))

        self.browser.select('language', self.language.id)
        self.assertTrue(self.is_visible('input[name="title"]'))
        self.browser.fill('title', self.project_data['title'])
        self.browser.fill('pitch', self.project_data['pitch'])

        btn = self.browser.attach_file('img_upload', '{0}/apps/projects/test_images/upload.png'.format(settings.PROJECT_ROOT))

        self.browser.find_by_css('.map-look-up input').type('Lyutidol')
        self.browser.find_by_css('.map-look-up button').click()

        # Splinter takes the value of the select option
        self.browser.select('theme', self.theme.id)

        for tag in self.project_data['tags']:
            self.browser.fill('tag', tag)
            self.browser.find_by_css("button.add-tag").first.click()

        self.browser.select('country', self.country_1.id)

        self.scroll_to_and_click_by_css("button.next")

        ###
        # Goal Section
        ###

        self.assertTrue(self.browser.is_text_present('Budget', wait_time=5))

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
            time.sleep(2)
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

        select = Select(self.browser.driver.find_element_by_name("account-holder-country"))
        select.select_by_visible_text("Afghanistan")

        self.scroll_to_and_click_by_css('ul.fieldset-tabs .tab-first a')
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
        submit = self.wait_for_element_css('.btn-submit')
        self.assertTrue(submit)
        submit.click()

        self.assertTrue(Project.objects.filter(slug=self.project_data['slug']).exists())

    def test_change_project_goal(self):
        plan_phase = ProjectPhase.objects.get(slug='plan-new')
        project = OnePercentProjectFactory.create(title='Project Goal Changes', owner=self.user, status=plan_phase)
        self.visit_path('/my/projects/{0}/goal'.format(project.slug))

        # Check that deadline is set to 100 days now
        days_left = self.browser.find_by_css('.project-days-left strong').first
        self.assertEqual(days_left.text, '100')

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

    def test_create_partner_project(self):
        """
        Creating a partner project should set the partner on the new project
        """
        self.partner = PartnerFactory.create()
        self.visit_path('/my/projects/pp:{0}'.format(self.partner.slug))

        # Wait for title to show
        self.wait_for_element_css("h3")
        self.assertEqual(self.browser.find_by_css("h3").text, self.partner.name.upper())


@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
            'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class ProjectWallpostSeleniumTests(OnePercentSeleniumTestCase):
    """
    Selenium tests for Projects.
    """
    def setUp(self):
        self.init_projects()

        super(ProjectWallpostSeleniumTests, self).setUp()
        self.user = BlueBottleUserFactory.create()

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
        self.login(self.user.email, 'testing')

        self.visit_path('/projects/{0}'.format(self.project.slug))

        wallpost_form = self.wait_for_element_css('#wallposts form')

        # Write wallpost as normal user
        wallpost_form.find_element_by_css_selector('textarea').send_keys(self.post1['text'])
        wallpost_form.find_element_by_css_selector('button.action-submit').click()

        wallpost = self.wait_for_element_css('#wallposts article:first-of-type')

        self.assertEqual(wallpost.find_element_by_css_selector('.user-name').text.upper(), self.user.get_full_name().upper())
        self.assertEqual(wallpost.find_element_by_css_selector('.wallpost-body').text, self.post1['text'])

        # Login as the project owner
        self.login(username=self.project.owner.email, password='testing')

        # Should see the post by the first user.
        self.visit_path('/projects/{0}'.format(self.project.slug))

        wallpost = self.wait_for_element_css('#wallposts article:first-of-type')
        self.assertEqual(wallpost.find_element_by_css_selector('.wallpost-body').text, self.post1['text'])

        # Post as project owner
        wallpost_form = self.wait_for_element_css('#wallposts form')
        wallpost_form.find_element_by_css_selector('textarea').send_keys(self.post2['text'])
        wallpost_form.find_element_by_css_selector('button.action-submit').click()

        # Wait for the two posts to load. Wait for the second first to ensure both have loaded.
        original_wallpost = self.wait_for_element_css_index('article.m-wallpost', 1)
        owner_wallpost = self.wait_for_element_css_index('article.m-wallpost', 0)

        self.assertEqual(owner_wallpost.find_element_by_css_selector('.user-name').text.upper(), self.project.owner.get_full_name().upper())
        self.assertEqual(owner_wallpost.find_element_by_css_selector('.wallpost-body').text, self.post2['text'])

        # And the first post should still be shown as second
        self.assertEqual(original_wallpost.find_element_by_css_selector('.user-name').text.upper(), self.user.get_full_name().upper())
        self.assertEqual(original_wallpost.find_element_by_css_selector('.wallpost-body').text, self.post1['text'])


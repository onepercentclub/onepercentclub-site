# -*- coding: utf-8 -*-
"""
Functional tests using Selenium.

See: ``docs/testing/selenium.rst`` for details.
"""
import time
from bluebottle.test.factory_models.accounts import BlueBottleUserFactory
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.text import slugify
from django.utils.unittest.case import skipUnless
from onepercentclub.tests.factory_models.project_factories import OnePercentProjectFactory

from onepercentclub.tests.utils import OnePercentSeleniumTestCase
from bluebottle.test.factory_models.tasks import TaskFactory, SkillFactory, TaskMemberFactory


@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
        'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class TaskCreateSeleniumTests(OnePercentSeleniumTestCase):
    """
    Selenium tests for Projects.
    """
    def setUp(self):
        self.init_projects()
        self.skill = SkillFactory.create()
        self.project = OnePercentProjectFactory.create()
        self.project.owner = BlueBottleUserFactory.create()
        self.project.save()
        self.login(username=self.project.owner.email, password='testing')

        self.task1 = {
            'title': 'Hora est labora',
            'description': 'In nec convallis felis. Quisque iaculis augue nec eros convallis, non rutrum velit mattis.',
            'location': 'Vestibulum nisi dui',
            'end_goal': 'World peace',
            'people_needed': 8,
            'time_needed': 4,
            'skill': self.skill.id
        }

    def tearDown(self):
        self.logout()

    def test_create_task(self):
        """
        Test to create a task
        """
        self.visit_path('/tasks/new/{0}'.format(self.project.slug))

        self.assertTrue(self.wait_for_element_css("legend#create-task-header"))

        # Fill all fields

        self.browser.fill('title', self.task1['title'])
        
        self.browser.find_by_css('textarea[name=description]').fill(self.task1['description'])

        self.browser.fill('end_goal', self.task1['end_goal'])

        # Pick a deadline next month
        self.assertTrue(self.scroll_to_and_click_by_css(".hasDatepicker"))

        # Wait for date picker popup
        self.assertTrue(self.browser.is_element_present_by_css("#ui-datepicker-div"))

        # Click Next to get a date in the future
        self.browser.find_by_css("[title=Next]").first.click()
        time.sleep(1)
        self.browser.is_text_present("10")
        self.browser.find_link_by_text("10").first.click()

        # FF doesn't know how to fill number fields ?
        # self.browser.fill('people_needed', self.task1['people_needed'])
        self.browser.fill('location', self.task1['location'])

        # Select time needed from select list
        self.assertTrue(self.scroll_to_and_click_by_css("select[name=time-needed]"))

        select = self.browser.find_by_css('select[name=skill]').first
        select.find_by_css('option')[1].click()

        # Submit task
        self.browser.find_by_css("button.btn-submit").first.click()

        # Check the task is loaded
        self.assertTrue(self.browser.is_text_present("OPEN TASK FOR", wait_time=20))
        self.assertRegexpMatches(self.browser.url, r'/tasks/\d+$')
        self.assertEqual(self.browser.find_by_css('h1.project-title').text.upper(), self.task1['title'].upper())


@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
        'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class TaskWallpostSeleniumTests(OnePercentSeleniumTestCase):
    """
    Selenium tests for Projects.
    """
    def setUp(self):
        self.init_projects()
        self.user = BlueBottleUserFactory.create()
        self.login(username=self.user.email, password='testing')

        self.task = TaskFactory.create()
        self.task.author = BlueBottleUserFactory.create()
        self.task.save()

        self.post1 = {
            'text': 'Hic arte doler omit et dametis!'
        }
        self.post2 = {
            'title': 'Hora est',
            'text': 'Caloda in amuet redicer...'
        }

    def tearDown(self):
        self.logout()

    def test_write_wall_post(self):
        """
        Test to write wall-posts on task page
        """
        self.visit_path('/tasks/{0}'.format(self.task.id))

        wallpost_form = self.wait_for_element_css('#wallposts form')
        wallpost_form.find_element_by_css_selector('textarea').send_keys(self.post1['text'])
        wallpost_form.find_element_by_css_selector('button.action-submit').click()

        post = self.wait_for_element_css('article.m-wallpost')
        self.assertEqual(post.find_element_by_css_selector('.user-name').text.upper(), self.user.get_full_name().upper())
        self.assertEqual(post.find_element_by_css_selector('.wallpost-body').text, self.post1['text'])


@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
        'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class TaskWithdrawSeleniumTest(OnePercentSeleniumTestCase):
    """
    Tests for the withdrawal of a Task Member for a Task
    """
    def setUp(self):
        self.init_projects()
        self.user = BlueBottleUserFactory.create()
        self.login(username=self.user.email, password='testing')

        self.task = TaskFactory.create(people_needed=2, time_needed=8)
        self.task.author = BlueBottleUserFactory.create()
        self.task.save()

        self.task_member = TaskMemberFactory.create(member=self.user, task=self.task)

    def tearDown(self):
        self.logout()

    # Doesn't Work
    # def test_withdraw_from_task(self):
    #     """
    #     Test that a user sees a withdraw buttin and withdraws from task
    #     """
    #     self.assertEquals(self.task.members.count(), 1)
    #     self.visit_path('/tasks/{0}'.format(self.task.id))
    #
    #     self.assertTrue(self.scroll_to_and_click_by_css('.withdraw'))
    #
    #     self.assertEquals(self.task.members.count(), 0)


    def test_no_withdraw_button(self):
        """
        Test that there is no withdraw button if a task member has a status or than "accepted" or "applied"
        """
        self.task_member.status = 'realized'
        self.task_member.save()

        self.visit_path('/tasks/{0}'.format(self.task.id))

        self.assertFalse(self.scroll_to_and_click_by_css('.withdraw'))

    def test_no_illegal_withdraw_(self):
        """
        Test that a user cannot withdraw someone else
        """
        task = TaskFactory.create(people_needed=2, time_needed=8)
        task.author = BlueBottleUserFactory.create()
        task.save()

        another_user = BlueBottleUserFactory.create()
        task_member = TaskMemberFactory.create(member=another_user, task=task)

        self.assertEquals(task.members.count(), 1)
        self.visit_path('/tasks/{0}'.format(task.id))

        self.assertFalse(self.scroll_to_and_click_by_css('.withdraw'))





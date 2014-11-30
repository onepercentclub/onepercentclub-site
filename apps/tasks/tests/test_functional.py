# -*- coding: utf-8 -*-
"""
Functional tests using Selenium.

See: ``docs/testing/selenium.rst`` for details.
"""
import time
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.text import slugify
from django.utils.unittest.case import skipUnless

from utils.tests.utils import BookingSeleniumTestCase
from utils.tests.factory_models.members_factories import BookingUserFactory
from utils.tests.factory_models.booking_projects_factories import BookingProjectFactory
from bluebottle.test.factory_models.tasks import TaskFactory, SkillFactory, TaskMemberFactory


@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
        'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class TaskCreateSeleniumTests(BookingSeleniumTestCase):
    """
    Selenium tests for Projects.
    """
    def setUp(self):
        self.init_projects()
        self.skill = SkillFactory.create()
        self.project = BookingProjectFactory.create()
        self.project.owner = BookingUserFactory.create()
        self.project.save()
        self.login_user(self.project.owner)


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

        self.assertDatePicked()





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
        self.assertTrue(self.browser.is_text_present("Task open", wait_time=20))
        self.assertRegexpMatches(self.browser.url, r'/tasks/\d+$')
        self.assertEqual(self.browser.find_by_css('h1.task-title').text, self.task1['title'])


@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
        'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class TaskWallPostSeleniumTests(BookingSeleniumTestCase):
    """
    Selenium tests for Projects.
    """
    def setUp(self):
        self.init_projects()
        self.user = BookingUserFactory.create()
        self.login_user(self.user)

        self.task = TaskFactory.create()
        self.task.author = BookingUserFactory.create()
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
        self.assertTrue(self.browser.is_text_present(self.task.title, wait_time=20))
        self.assertTrue(self.browser.is_text_present('Post a new comment on wall', wait_time=20))

        self.browser.find_by_css(".wallpost-post-update").click()
        self.assertTrue(self.browser.is_text_present('Post', wait_time=20))

        # Write wallpost as normal user
        self.browser.fill('wallpost-update', self.post1['text'])

        self.browser.find_by_css("button.btn-save").first.click()

        post = self.browser.find_by_css("article.wallpost").first

        self.assertEqual(post.find_by_css('.wallpost-author').text, self.user.short_name)
        self.assertEqual(post.find_by_css('.text p').text, self.post1['text'])

        self.logout()

        # Login as the task author
        self.login_user(self.task.author)

        # Should see the post by the first user.
        self.visit_path('/tasks/{0}'.format(self.task.id))
        self.assert_css('article.wallpost')
        post = self.browser.find_by_css("article.wallpost").first
        self.assertEqual(post.find_by_css('.wallpost-author').text, self.user.short_name)

        self.assertEqual(post.find_by_css('.text p').text, self.post1['text'])

        # Post as task author
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

        self.assertEqual(post.find_by_css('.wallpost-author').text, self.task.author.short_name)
        self.assertEqual(post.find_by_css('.wallpost-title').text, self.post2['title'])
        self.assertEqual(post.find_by_css('.text p').text, self.post2['text'])

        # And the first post shoulkd still be shown as second
        post = self.browser.find_by_css("article.wallpost")[1]
        self.assertEqual(post.find_by_css('.wallpost-author').text, self.user.short_name)
        self.assertEqual(post.find_by_css('.text p').text, self.post1['text'])


@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
        'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class TaskImpact(BookingSeleniumTestCase):
    """
    Selenium tests for the task realized and hours spent vlaues on the homepage
    """
    def setUp(self):
        self.init_projects()
        self.user = BookingUserFactory.create()
        self.login_user(self.user)

        self.task = TaskFactory.create()
        self.task.author = BookingUserFactory.create()
        self.task.time_needed = 8
        self.task.save()

        self.task_member = TaskMemberFactory(task=self.task)
        self.task_member.status = 'realized'
        self.task_member.save()

        self.task_member2 = TaskMemberFactory(task=self.task)
        self.task_member2.status = 'realized'
        self.task_member2.save()

        self.task2 = TaskFactory.create()
        self.task2.time_needed = 8
        self.task2.author = BookingUserFactory.create()
        self.task2.save()

        self.task_member3 = TaskMemberFactory(task=self.task2)

        self.task_member3.status = 'applied'
        self.task_member3.save()

    def tearDown(self):
        self.logout()

    def test_impact_values(self):
        self.visit_homepage('en')
        self.assert_css('.impact-tasks')
 
        #Setup creates 3 task members for the same task. The task has 8 estimated hrs.
        #2 taskmembers have a "realized" status, so their hours are counted.

        #Both task members work on the same task, so the task counter should say one task
        tasks_realized = self.scroll_to_by_css('.impact-tasks strong')
        self.assertEqual(tasks_realized.text, "1")

        impact_hours = self.browser.find_by_css(".impact-hours strong")
        self.assertEqual(impact_hours.text, "16")

    def test_impact_values_updated(self):
        self.task_member3.status = 'realized'
        self.task_member3.save()

        self.visit_homepage('en')

        tasks_realized = self.scroll_to_by_css('.impact-tasks strong')
        #There are now two tasks
        self.assertEqual(tasks_realized.text, "2")

        impact_hours = self.scroll_to_by_css(".impact-hours strong")
        #There are three task members with a realized task --> 24hrs total
        self.assertEqual(impact_hours.text, "24")

    def test_impact_values_employee_count(self):
        self.task_member3.status = 'accepted'
        self.task_member3.save()

        self.visit_homepage('en')

        #All task members with status accepted or realized
        employees = self.scroll_to_by_css(".impact-employees strong")
        self.assertEqual(employees.text, "3")


@skipUnless(getattr(settings, 'SELENIUM_TESTS', False),
        'Selenium tests disabled. Set SELENIUM_TESTS = True in your settings.py to enable.')
class TaskWithdrawSeleniumTest(BookingSeleniumTestCase):
    """
    Tests for the withdrawal of a Task Member for a Task
    """
    def setUp(self):
        self.init_projects()
        self.user = BookingUserFactory.create()
        self.login_user(self.user)

        self.task = TaskFactory.create(people_needed=2, time_needed=8)
        self.task.author = BookingUserFactory.create()
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
        task.author = BookingUserFactory.create()
        task.save()

        another_user = BookingUserFactory.create()
        task_member = TaskMemberFactory.create(member=another_user, task=task)

        self.assertEquals(task.members.count(), 1)
        self.visit_path('/tasks/{0}'.format(task.id))

        self.assertFalse(self.scroll_to_and_click_by_css('.withdraw'))





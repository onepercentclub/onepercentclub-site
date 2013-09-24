from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from bluebottle.bluebottle_utils.tests import generate_random_slug
from apps.projects.tests import ProjectTestsMixin
from .models import Task
import json


class TaskTestsMixin(ProjectTestsMixin):
    """ Mixin base class for tests using tasks. """

    def create_task(self, owner=None, project=None, title='', description='', status='open'):
        """
        Create a 'default' task with some standard values but allow for overrides.
        The returned object is saved to the database.
        """

        if not owner:
            # Create a new user with a random username
            owner = self.create_user()

        if not project:
            # Create a new project
            owner = self.create_project()

        if not title:
            title = generate_random_slug()

        if not description:
            title = generate_random_slug()

        task = Task(
            owner=owner, title=title, status=status, project=project
        )

        task.save()

        return task


class TaskApiIntegrationTests(TestCase, TaskTestsMixin):
    """ Tests for tasks. """

    def setUp(self):
        self.some_user = self.create_user()
        self.another_user = self.create_user()

        self.some_project = self.create_project(owner=self.some_user)
        self.another_project = self.create_project(owner=self.another_user)

        self.task_url = '/api/tasks/'
        self.task_members_url = '/api/tasks/members/'

    def test_create_task(self):

        self.client.login(username=self.some_user.email, password='password')

        # Get the list of tasks for some project should return none (count = 0)
        response = self.client.get(self.task_url, {'project': self.some_project.slug})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEquals(response.data['count'], 0)

        future_date = timezone.now() + timezone.timedelta(days=30)

        # Now let's create a task.
        some_task_data = {'project': self.some_project.slug, 'title': 'A nice task!',
                          'description': 'Well, this is nice', 'time_needed': 5, 'skill': '1',
                          'location': 'Overthere', 'deadline' : future_date, 'end_goal': 'World peace'}
        response = self.client.post(self.task_url, some_task_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEquals(response.data['title'], some_task_data['title'])
        some_task_url = "{0}{1}".format(self.task_url, response.data['id'])

        # Create a task for a project you don't own should fail...
        another_task_data = {'project': self.another_project.slug, 'title': 'Translate some text.',
                          'description': 'Wie kan in engels vertalen?', 'time_needed': 5, 'skill': '4',
                          'location': 'Tiel', 'deadline' : future_date, 'end_goal': 'World peace'}
        response = self.client.post(self.task_url, another_task_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

        # By now the list for this project should contain one task
        response = self.client.get(self.task_url, {'project': self.some_project.slug})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEquals(response.data['count'], 1)

        self.client.logout()
        self.client.login(username=self.another_user.email, password='password')

        # Another user that owns another project can create a task for that.
        another_task_data = {'project': self.another_project.slug, 'title': 'Translate some text.',
                          'description': 'Wie kan Engels vertalen?', 'time_needed': 5, 'skill': '12',
                          'location': 'Tiel', 'deadline' : future_date, 'end_goal': 'World peace'}
        response = self.client.post(self.task_url, another_task_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEquals(response.data['title'], another_task_data['title'])

        # Go wild! Add another task to that project add some tags this time
        # Because we have a nesting here we should properly encode it as json
        third_task_data = {'project': self.another_project.slug, 'title': 'Translate some text.',
                           'description': 'Wie kan Engels vertalen?', 'time_needed': 5, 'skill': '3',
                           'location': 'Tiel', 'deadline': str(future_date), 'end_goal': 'World peace',
                           'tags': [{'id': 'spanish'}, {'id': 'translate'}]}
        response = self.client.post(self.task_url, json.dumps(third_task_data), 'application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEquals(response.data['title'], third_task_data['title'])
        self.assertEquals(len(response.data['tags']), 2)

        # By now the list for the second project should contain two tasks
        response = self.client.get(self.task_url, {'project': self.another_project.slug})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEquals(response.data['count'], 2)

        # Viewing task detail for the first task (other owner) should work
        response = self.client.get(some_task_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEquals(response.data['title'], some_task_data['title'])

    def test_apply_for_task(self):

        self.client.login(username=self.some_user.email, password='password')

        future_date = timezone.now() + timezone.timedelta(days=60)

        # let's create a task.
        some_task_data = {'project': self.some_project.slug, 'title': 'A nice task!',
                          'description': 'Well, this is nice', 'time_needed': 5, 'skill': '4',
                          'location': 'Overthere', 'deadline': future_date, 'end_goal': 'World peace'}
        response = self.client.post(self.task_url, some_task_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        self.client.logout()
        self.client.login(username=self.another_user.email, password='password')

        response = self.client.post(self.task_members_url, {'task': 1})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEquals(response.data['status'], 'applied')



# TODO: Test edit task
# TODO: Test change TaskMember edit status
# TODO: Test File uploads




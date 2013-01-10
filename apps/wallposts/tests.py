from django.test import TestCase
from rest_framework import status
from apps.projects.tests import ProjectTestsMixin

class ProjectWallpostApiIntegrationTest(ProjectTestsMixin, TestCase):
    """
    Integration tests for the ProjectWallPost API.
    """
    def setUp(self):

        self.some_user = self.create_user()
        self.some_user.save()

        self.another_user = self.create_user()
        self.another_user.save()

        self.project = self.create_project()
        self.project.save()

        self.anotherproject = self.create_project()
        self.anotherproject.save()

        self.wallposts_url = '/i18n/api/wallposts/projectwallposts/'
        self.mediawallposts_url = '/i18n/api/wallposts/projectmediawallposts/'
        self.textwallposts_url = '/i18n/api/wallposts/projecttextwallposts/'


    def tearDown(self):
        self.client.logout()

    def test_projecttextwallpost_crud(self):
        """
        Tests for creating, retrieving, updating and deleting wallposts
        """

        # Create text wallpost as not logged in guest should be denied
        text1 = 'Great job!'
        response = self.client.post(self.textwallposts_url, {'text': text1, 'project_id': self.project.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

        self.client.login(username=self.some_user.username, password='password')

        # Create TextWallPost as a logged in member should be allowed
        response = self.client.post(self.textwallposts_url, {'text': text1, 'project_id': self.project.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['text'], text1)

        # Retrieve text wallpost through WallPosts api
        wallpost_detail_url = "{0}{1}".format(self.wallposts_url, str(response.data['id']))
        response = self.client.get(wallpost_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['text'], text1)

        # Retrieve text wallpost through TextWallPosts api
        wallpost_detail_url = "{0}{1}".format(self.textwallposts_url, str(response.data['id']))
        response = self.client.get(wallpost_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['text'], text1)

        self.client.logout()
        self.client.login(username=self.another_user.username, password='password')

        # Retrieve text wallpost through projectwallposts api by another user
        wallpost_detail_url = "{0}{1}".format(self.wallposts_url, str(response.data['id']))
        response = self.client.get(wallpost_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['text'], text1)

        # Create TextWallPost without a text should return an error and
        response = self.client.post(self.textwallposts_url, {'text': '', 'project_id': self.project.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertIsNotNone(response.data['text'])

        text2 = "I liek this project!"

        # Create TextWallPost as another logged in member should be allowed
        response = self.client.post(self.textwallposts_url, {'text': text2, 'project_id': self.project.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['text'], text2)


        # Update TextWallPost by author is allowed
        text2a = 'I like this project!'
        wallpost_detail_url = "{0}{1}".format(self.textwallposts_url, str(response.data['id']))
        response = self.client.put(wallpost_detail_url, {'text': text2a, 'project_id': self.project.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['text'], text2a)

        self.client.logout()
        self.client.login(username=self.some_user.username, password='password')

        # Update TextWallPost by another user (not the author) is allowed
        text2b = 'Mess this up!'
        wallpost_detail_url = "{0}{1}".format(self.textwallposts_url, str(response.data['id']))
        response = self.client.put(wallpost_detail_url, {'text': text2b, 'project_id': self.project.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)


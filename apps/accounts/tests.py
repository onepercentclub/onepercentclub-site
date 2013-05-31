from django.test import TestCase
from apps.bluebottle_utils.tests import UserTestsMixin
from django.test.client import BOUNDARY, encode_multipart, MULTIPART_CONTENT
from rest_framework import status


class UserApiIntegrationTest(UserTestsMixin, TestCase):
    """
    Integration tests for the User API.
    """
    def setUp(self):
        self.some_user = self.create_user(first_name='Nijntje')
        self.some_user.email = 'nijntje@hetkonijnje.nl'
        self.some_user.save()
        self.another_user = self.create_user()
        self.current_user_api_url = '/i18n/api/users/current'
        self.user_create_api_url = '/i18n/api/users/'
        self.user_profile_api_url = '/i18n/api/users/profiles/'
        self.user_settings_api_url = '/i18n/api/users/settings/'

    def test_user_profile_retrieve_and_update(self):
        """
        Test retrieving a public user profile by id.
        """
        user_profile_url = "{0}{1}".format(self.user_profile_api_url, self.some_user.id)
        response = self.client.get(user_profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.some_user.id)

        # Profile should be able to be updated after by logged in user.
        self.client.login(username=self.some_user.username, password='password')
        full_name = {'first_name': 'Nijntje', 'last_name': 'het Konijnje'}
        response = self.client.put(user_profile_url, encode_multipart(BOUNDARY, full_name), MULTIPART_CONTENT)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['first_name'], full_name.get('first_name'))
        self.assertEqual(response.data['last_name'], full_name.get('last_name'))

        self.client.logout()

    def test_unauthenticated_user(self):
        """
        Test retrieving the currently logged in user while not logged in.
        """
        # Test unauthenticated user doesn't return 500 error.
        response = self.client.get(self.current_user_api_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

    def test_current_user(self):
        """
        Test retrieving the currently logged in user after login.
        """
        self.client.login(username=self.some_user.email, password='password')
        response = self.client.get(self.current_user_api_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['first_name'], self.some_user.first_name)

        self.client.logout()

    def test_user_settings_retrieve(self):
        """
        Test retrieving a user's settings by id.
        """
        # Settings shouldn't be accessible until a user is logged in.
        user_settings_url = "{0}{1}".format(self.user_settings_api_url, self.some_user.id)
        response = self.client.get(user_settings_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_user_create_and_update_settings(self):
        """
        Test creating a user with the api.
        """
        # Create a user.
        new_user_email = 'nijntje27@hetkonijnje.nl'
        new_user_password = 'hetkonijnje'
        response = self.client.post(self.user_create_api_url, {'email': new_user_email,
                                                               'password': new_user_password})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        user_id = response.data['id']

        # Login and getting the settings should work.
        self.client.login(email=new_user_email, password=new_user_password)
        new_user_settings_url = "{0}{1}".format(self.user_settings_api_url, user_id)
        response = self.client.get(new_user_settings_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['email'], new_user_email)
        self.assertFalse(response.data['newsletter'])

        # Test that the settings can be updated.
        response = self.client.put(new_user_settings_url, encode_multipart(BOUNDARY, {'newsletter': True}), MULTIPART_CONTENT)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTrue(response.data['newsletter'])

        self.client.logout()

        # Test that the email field is required on user create.
        response = self.client.post(self.user_create_api_url, {'password': new_user_password})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertEqual(response.data['email'][0], 'This field is required.')
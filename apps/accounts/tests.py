from django.test import TestCase
from apps.accounts.models import UserProfile, UserProfileCreationError
from apps.bluebottle_utils.tests import UserTestsMixin
from rest_framework import status


class UserProfileTestCase(UserTestsMixin, TestCase):
    """ Tests for the UserProfile model. """

    def test_slug_update(self):
        """
        This test checks that UserProfile.slug is updated when User.username changed.
        """
        # Check that the slug is the same as the username.
        test_username1 = 'testuser23'

        user = self.create_user(username=test_username1)

        profile = user.get_profile()
        self.assertEqual(test_username1, profile.slug)

        # Check that the slug is the same as the changed username.
        test_username2 = 'testuser'
        user.username = test_username2
        user.save()
        self.assertEqual(test_username2, profile.slug)

    def test_create_without_user(self):
        """
        This test checks that creating a UserProfile object correctly throws
        an exception as this operation is prohibited.
        """
        user_profile = UserProfile()
        self.assertRaises(UserProfileCreationError, user_profile.save)


class UserApiIntegrationTest(UserTestsMixin, TestCase):
    """
    Integration tests for the User API.
    """
    def setUp(self):
        self.some_user = self.create_user(username='someuser')
        self.some_user.email = 'nijntje@hetkonijnje.nl'
        self.some_user.save()
        self.another_user = self.create_user(username='anotheruser')
        self.current_user_api_url = '/i18n/api/users/current'
        self.user_api_url = '/i18n/api/users/'
        self.user_settings_api_url = '/i18n/api/users/settings/'

    def test_user_profile_retrieve(self):
        """
        Test retrieving a public user profile by id.
        """
        user_profile_url = "{0}{1}".format(self.user_api_url, self.some_user.id)
        response = self.client.get(user_profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.some_user.username)

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
        self.client.login(username=self.some_user.username, password='password')
        response = self.client.get(self.current_user_api_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['username'], self.some_user.username)

        self.client.logout()

    def test_user_settings_retrieve(self):
        """
        Test retrieving a user's settings by id.
        """
        # Settings shouldn't be accessible until a user is logged in.
        user_settings_url = "{0}{1}".format(self.user_settings_api_url, self.some_user.id)
        response = self.client.get(user_settings_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

        # Settings should be accessible after logging in.
        self.client.login(username=self.some_user.username, password='password')
        response = self.client.get(user_settings_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['email'], self.some_user.email)

        # Only the logged in user should be able to read the settings.
        user_settings_url = "{0}{1}".format(self.user_settings_api_url, self.another_user.id)
        response = self.client.get(user_settings_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

        self.client.logout()

    # FIXME: Will be fixed with the new user creation api.
    # def test_user_create(self):
    #     """
    #     Test creating a user with the api.
    #     """
    #     # Create a user.
    #     new_user_username = 'nijntje'
    #     new_user_password = 'hetkonijnje'
    #     new_user_email = 'nijntje@hetkonijnje.nl'
    #     response = self.client.post(self.user_api_url, {'username': new_user_username,
    #                                                            'password': new_user_password,
    #                                                            'email': new_user_email})
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
    #     user_id = response.data['id']
    #
    #     # Login and getting the settings should work.
    #     self.client.login(username=new_user_username, password=new_user_password)
    #     new_user_settings_url = "{0}{1}".format(self.user_settings_api_url, user_id)
    #     response = self.client.get(new_user_settings_url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
    #     self.assertEqual(response.data['email'], new_user_email)
    #     self.assertFalse(response.data['newsletter'])
    #
    #     # Test that the settings can be updated.
    #     response = self.client.put(new_user_settings_url, {'newsletter': True})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
    #     self.assertTrue(response.data['newsletter'])
    #
    #     self.client.logout()
    #
    #     # Test that the email field is required on user create.
    #     response = self.client.post(self.user_api_url, {'username': new_user_username,
    #                                                            'password': new_user_password})
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
    #     self.assertEqual(response.data['email'][0], 'This field is required.')
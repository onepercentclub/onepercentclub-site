from django.test import TestCase
from apps.accounts.models import UserProfile, UserProfileCreationError
from apps.bluebottle_utils.tests import UserTestsMixin
from rest_framework import status


class UserProfileTestCase(UserTestsMixin, TestCase):
    """ Tests for the UserProfile model. """

    def test_slug_update(self):
        """
        This test checks that UserProfile.slug is updated when User.username
        changed.
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

        # Test a fail
        user_profile = UserProfile()

        self.assertRaises(UserProfileCreationError, user_profile.save)


class MemberApiIntegrationTest(UserTestsMixin, TestCase):
    """
    Integration tests for the BlogPost API.
    """

    def setUp(self):
        self.some_user = self.create_user(username='someuser')
        self.another_user = self.create_user(username='anotheruser')
        self.member_api_url = '/i18n/api/members/'
        self.private_member_api_url = '/i18n/api/members/settings/'

    def test_user_retrieve(self):
        """
        Test retrieving a user by id.
        """

        user_detail_url = "{0}{1}".format(self.member_api_url, self.some_user.id)
        response = self.client.get(user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['username'], self.some_user.username)

    def test_unauthenticated_member(self):
        """
        Test retrieving the currently logged in user while not logged in
        """

        # Test unauthenticated user doesn't return 500 error.
        authenticated_member_url = "{0}{1}".format(self.member_api_url, 'current')
        response = self.client.get(authenticated_member_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)


    def test_authenticated_member(self):
        """
        Test retrieving the currently logged in user after login.
        """

        self.client.login(username=self.some_user.username, password='password')
        authenticated_member_url = "{0}{1}".format(self.member_api_url, 'current')
        response = self.client.get(authenticated_member_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['username'], self.some_user.username)



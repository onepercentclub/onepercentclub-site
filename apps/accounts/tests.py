from apps.accounts.views import MemberList, MemberDetail
from django.test import TestCase
from apps.accounts.models import User
from apps.bluebottle_utils.tests import UserTestsMixin
from rest_framework import status

class MemberApiIntegrationTest(UserTestsMixin, TestCase):
    """
    Integration tests for the BlogPost API.
    """

    def setUp(self):
        self.user = self.create_user()
        self.list_view = MemberList.as_view()
        self.detail_view = MemberDetail.as_view()
        self.member_api_base_url = '/i18n/api/members/'


    def test_user_retrieve(self):
        """
        Test retrieving a user by id.
        """

        user_detail_url = "{0}{1}{2}".format(self.member_api_base_url, 'users/', self.user.id)
        response = self.client.get(user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['username'], self.user.username)


    def test_authenticated_member(self):
        """
        Test retrieving the currently logged in user.
        """

        # Test unauthenticated user doesn't return 500 error.
        authenticated_member_url = "{0}{1}".format(self.member_api_base_url, 'current')
        response = self.client.get(authenticated_member_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['username'], '')

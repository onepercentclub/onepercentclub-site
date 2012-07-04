from django.utils import unittest
from django.contrib.auth.models import User


class UserProfileTestCase(unittest.TestCase):
    def test_slug_update(self):
        """
        This test checks that UserProfile.slug is updated when User.username
        changed.
        """
        # Check that the slug is the same as the username.
        test_username1 = 'testuser23'
        user = User(username=test_username1)
        user.save()
        profile = user.get_profile()
        self.assertEqual(test_username1, profile.slug)

        # Check that the slug is the same as the changed username.
        test_username2 = 'testuser'
        user.username = test_username2
        user.save()
        self.assertEqual(test_username2, profile.slug)

        # Remove the test user.
        user.delete()

from django.contrib.auth.models import User
from django.utils import unittest

from apps.accounts.models import UserProfile, UserProfileCreationError


class UserProfileTestCase(unittest.TestCase):
    """ Tests for the UserProfile model. """

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

    def test_create_without_user(self):
        """
        This test checks that creating a UserProfile object correctly throws an
        exception as this operation is prohibited.
        """

        user_profile = UserProfile()
        # This somewhat awkward test strategy is used because AssertRaises is
        # not working for some reason.
        try:
            user_profile.save()
        except UserProfileCreationError:
            pass
        except:
            raise
        else:
            self.fail("Expected exception not thrown.")

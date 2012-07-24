from django.utils.unittest import TestCase

from apps.accounts.models import UserProfile, UserProfileCreationError

from apps.bluebottle_utils.tests import UserTestsMixin


class UserProfileTestCase(TestCase, UserTestsMixin):
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

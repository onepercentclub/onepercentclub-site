from django.test import TestCase

from django.contrib.auth.models import User


class LegacyHashTest(TestCase):
    def setUp(self):
        """
        Create a new user with old-style hash.
        """

        user = User(
            username='barbabob',
            email='bob@barbapappa.com',
            # Password is huubhuubbarbatruuk
            password='legacy$fd054714ea93060e80c3cac98ff47a424a2acfd1'
        )

        user.save()

    def test_success(self):
        """ Test whether we can login with a legacy hash password. """

        login_result = self.client.login(
            username='barbabob',
            password='huubhuubbarbatruuk'
        )
        self.assertTrue(login_result)

    def test_fail(self):
        """ Test whether a wrong password yields a big fail. """

        login_result = self.client.login(
            username='barbabob',
            password='plopperdeplop'
        )
        self.assertFalse(login_result)

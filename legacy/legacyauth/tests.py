from django.test import TestCase

from django.contrib.auth.models import User


class LegacyHashTest(TestCase):
    """ Test login functionality for legacy hashes. """

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

    def test_rehash(self):
        """
        Test whether a user's password is rehashed during login.
        """

        # Just test the test
        user = User.objects.get(username='barbabob')
        algo = user.password.split('$', 1)[0]

        self.assertEqual(algo, 'legacy')

        self.client.login(
            username='barbabob',
            password='huubhuubbarbatruuk'
        )

        # Should be a different algo here
        user = User.objects.get(username='barbabob')
        algo = user.password.split('$', 1)[0]

        self.assertNotEqual(algo, 'legacy')

        # Login should still work
        login_result = self.client.login(
            username='barbabob',
            password='huubhuubbarbatruuk'
        )
        self.assertTrue(login_result)


class EmailLoginTest(TestCase):
    """ Test login functionality for email addresses. """

    def setUp(self):
        """
        Create a new user.
        """

        user = User(
            username='barbabob',
            email='bob@barbapappa.com',
        )

        user.set_password('huubhuubbarbatruuk')

        user.save()

    def test_success(self):
        """ Test whether we can login with a legacy hash password. """

        login_result = self.client.login(
            username='bob@barbapappa.com',
            password='huubhuubbarbatruuk'
        )
        self.assertTrue(login_result)

    def test_fail(self):
        """ Test whether a wrong password yields a big fail. """

        login_result = self.client.login(
            username='bob@barbapappa.com',
            password='plopperdeplop'
        )
        self.assertFalse(login_result)

    def test_legacy(self):
        """ Test whether a legacy user can login with email as well. """

        user2 = User(
            username='barbapappa',
            email='pappa@barbapappa.com',
            # Password is huubhuubbarbatruuk
            password='legacy$fd054714ea93060e80c3cac98ff47a424a2acfd1'
        )

        user2.save()

        login_result = self.client.login(
            username='pappa@barbapappa.com',
            password='huubhuubbarbatruuk'
        )
        self.assertTrue(login_result)


    def test_legacyrehash(self):
        """ Test whether a legacy email user get's his password reset. """

        user2 = User(
            username='barbapappa',
            email='pappa@barbapappa.com',
            # Password is huubhuubbarbatruuk
            password='legacy$fd054714ea93060e80c3cac98ff47a424a2acfd1'
        )

        user2.save()

        self.client.login(
            username='pappa@barbapappa.com',
            password='huubhuubbarbatruuk'
        )

        # Should be a different algo here
        user = User.objects.get(username='barbapappa')
        algo = user.password.split('$', 1)[0]

        self.assertNotEqual(algo, 'legacy')

import uuid

from django.contrib.auth.models import User
from django.core.management import call_command
from django.db.models import loading
from django.test import TestCase
from django.test.utils import override_settings


def generate_random_slug():
    return str(uuid.uuid4())[:30]


class UserTestsMixin(object):
    """ Mixin base class for tests requiring users. """

    def create_user(self, username=None, password=None):
        """ Create, save and return a new user. """

        # If username is set and not unique, it will raise a clearly
        # interpretable IntegrityError.
        # If auto-generated, make sure it's unique.

        if not username:
            username = generate_random_slug()
            while User.objects.filter(username=username).exists():
                 username = generate_random_slug()

        user = User.objects.create_user(username=username)

        if not password:
            user.set_password('password')

        return user


class CustomSettingsTestCase(TestCase):
    """
    A TestCase which makes extra models available in the Django project, just for testing.
    Based on http://djangosnippets.org/snippets/1011/ in Django 1.4 style.
    """
    new_settings = {}
    _override = None


    @classmethod
    def setUpClass(cls):
        cls._override = override_settings(**cls.new_settings)
        cls._override.enable()
        if 'INSTALLED_APPS' in cls.new_settings:
            cls.syncdb()


    @classmethod
    def tearDownClass(cls):
        cls._override.disable()
        if 'INSTALLED_APPS' in cls.new_settings:
            cls.syncdb()


    @classmethod
    def syncdb(cls):
        loading.cache.loaded = False
        call_command('syncdb', verbosity=0)

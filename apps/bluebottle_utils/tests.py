import uuid
from apps.accounts.models import BlueBottleUser
from django.core.management import call_command
from django.db.models import loading
from django.test import TestCase
from django.test.utils import override_settings


def generate_random_slug():
    return str(uuid.uuid4())[:30]


def generate_random_email():
    return str(uuid.uuid4())[:10] + '@' + str(uuid.uuid4())[:30] + '.com'


class UserTestsMixin(object):
    """ Mixin base class for tests requiring users. """

    def create_user(self, email=None, password=None, **extra_fields):
        """ Create, save and return a new user. """

        # If email is set and not unique, it will raise a clearly interpretable IntegrityError.
        # If auto-generated, make sure it's unique.
        if not email:
            email = generate_random_email()
            while BlueBottleUser.objects.filter(email=email).exists():
                email = generate_random_email()

        user = BlueBottleUser.objects.create_user(email=email, **extra_fields)

        if not password:
            user.set_password('password')

        user.save()

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


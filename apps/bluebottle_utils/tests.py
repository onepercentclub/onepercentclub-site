import uuid
from apps.accounts.models import BlueBottleUser
from apps.blogs.models import BlogPostProxy
from django.core.management import call_command
from django.db.models import loading
from django.test import TestCase
from django.test.utils import override_settings
from fluent_contents.models import Placeholder


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


class BlogPostCreationMixin(UserTestsMixin):

    def create_blogpost(self, title=None, slug=None, language=None, user=None):
        bp = BlogPostProxy()

        if not title:
            title = 'We Make it Work!'

        if not slug:
            slug = generate_random_slug()
            # Ensure generated slug is unique.
            while BlogPostProxy.objects.filter(slug=slug).exists():
                slug = generate_random_slug()

        if not language:
            language = 'nl'

        if not user:
            user = self.create_user()
            user.save()

        bp.title = title
        bp.language = language
        bp.slug = slug
        bp.author = user
        bp.save()

        # The contents needs to be created separately.
        ph = Placeholder.objects.create_for_object(bp, 'blog_contents')
        ph.save()

        return bp

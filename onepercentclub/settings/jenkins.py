
# SECRET_KEY and DATABASES needs to be defined before the base settings is imported.
SECRET_KEY = 'hbqnTEq+m7Tk61bvRV/TLANr3i0WZ6hgBXDh3aYpSU8m+E1iCtlU3Q=='

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

from .base import *

#
# Put jenkins environment specific overrides below.
#

INSTALLED_APPS += ('django_jenkins',)

DEBUG = False
TEMPLATE_DEBUG = False
INCLUDE_TEST_MODELS = True

# Test all INSTALLED_APPS by default
PROJECT_APPS = list(INSTALLED_APPS)

# Some of these tests fail, and it's not our fault
# https://code.djangoproject.com/ticket/17966
PROJECT_APPS.remove('django.contrib.auth')
PROJECT_APPS.remove('bluebottle.auth')
PROJECT_APPS.remove('legacyauth')

# Don't run Bluebottle tests
PROJECT_APPS.remove('bluebottle.bb_accounts')
PROJECT_APPS.remove('bluebottle.bb_organizations')
PROJECT_APPS.remove('bluebottle.bb_projects')
PROJECT_APPS.remove('bluebottle.bb_tasks')
PROJECT_APPS.remove('bluebottle.wallposts')
PROJECT_APPS.remove('bluebottle.utils')
PROJECT_APPS.remove('bluebottle.geo')

# This app fails with a strange error:
# DatabaseError: no such table: django_comments
# Not sure what's going on so it's disabled for now.
PROJECT_APPS.remove('django.contrib.sites')

# https://github.com/django-extensions/django-extensions/issues/154
PROJECT_APPS.remove('django_extensions')
PROJECT_APPS.remove('django_extensions.tests')
PROJECT_APPS.remove('django.contrib.messages')
PROJECT_APPS.remove('django.contrib.sessions')

PROJECT_APPS.remove('polymorphic')
PROJECT_APPS.remove('social.apps.django_app.default')

# django-registration tests don't pass with our Django 1.5 custom user model / manager.
PROJECT_APPS.remove('registration')

# django_fluent_contents 0.8.5 tests don't pass with a Django 1.5 custom user model.
PROJECT_APPS.remove('fluent_contents')
PROJECT_APPS.remove('fluent_contents.plugins.text')
PROJECT_APPS.remove('fluent_contents.plugins.oembeditem')
PROJECT_APPS.remove('fluent_contents.plugins.rawhtml')

# Disable pylint becasue it seems to be causing problems
JENKINS_TASKS = (
    # 'django_jenkins.tasks.run_pylint',
    'django_jenkins.tasks.with_coverage',
    'django_jenkins.tasks.django_tests',
)

# Selenium tests still disabled by default.
SELENIUM_TESTS = False
SELENIUM_WEBDRIVER = 'firefox'

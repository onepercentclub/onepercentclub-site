# Import default settings
from .defaults import *

# Import secrets
from .secrets import *

# Put your environment specific overrides below

INSTALLED_APPS.append('django_jenkins')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'onepercentsite',
        'USER': 'jenkins'
    }
}

# Test all INSTALLED_APPS by default
PROJECT_APPS = list(INSTALLED_APPS)

# Some of these tests fail, and it's not our fault
# https://code.djangoproject.com/ticket/17966
PROJECT_APPS.remove('django.contrib.auth')

# Don't run DRF2 tests for now because it's still in development and they fail.
# This is actually weird considering they are passing in Travis:
# https://travis-ci.org/#!/tomchristie/django-rest-framework
PROJECT_APPS.remove('rest_framework')

# https://github.com/django-extensions/django-extensions/issues/154
PROJECT_APPS.remove('django_extensions')
PROJECT_APPS.remove('django_extensions.tests')

# Disable pylint becasue it seems to be causing problems
JENKINS_TASKS = (
    # 'django_jenkins.tasks.run_pylint',
    'django_jenkins.tasks.with_coverage',
    'django_jenkins.tasks.django_tests',
)

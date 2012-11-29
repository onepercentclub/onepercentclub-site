# Import default settings
from .defaults import *

# Put jenkins specific overrides below

INSTALLED_APPS.append('django_jenkins')

SECRET_KEY = 'hbqnTEq+m7Tk61bvRV/TLANr3i0WZ6hgBXDh3aYpSU8m+E1iCtlU3Q=='

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

# Test all INSTALLED_APPS by default
PROJECT_APPS = list(INSTALLED_APPS)

# Some of these tests fail, and it's not our fault
# https://code.djangoproject.com/ticket/17966
PROJECT_APPS.remove('django.contrib.auth')

# https://github.com/django-extensions/django-extensions/issues/154
PROJECT_APPS.remove('django_extensions')
PROJECT_APPS.remove('django_extensions.tests')

# Disable pylint becasue it seems to be causing problems
JENKINS_TASKS = (
    # 'django_jenkins.tasks.run_pylint',
    'django_jenkins.tasks.with_coverage',
    'django_jenkins.tasks.django_tests',
)

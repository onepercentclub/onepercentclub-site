try:
    from .secrets import *
except ImportError:
    import sys
    sys.exit('secrets.py settings file not found. Please run `prepare.sh` to create one.')

from .base import *

#
# Put testing environment specific overrides below.
#

DEBUG = True
TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS += (
    'gunicorn',
    'django_nose',
)

COWRY_RETURN_URL_BASE = 'https://testing.onepercentclub.com'
COWRY_LIVE_PAYMENTS = False

# Send email for real
EMAIL_BACKEND = 'bluebottle.utils.email_backend.TestMailBackend'

SESSION_COOKIE_NAME = 'bb-testing-session-id'

SELENIUM_WEBDRIVER = 'chrome'


# We're using nose because it limits the tests to our apps (i.e. no Django and
# 3rd party app tests). We need this because tests in contrib.auth.user are
# failing in Django 1.4.1. Here's the ticket for the failing test:
# https://code.djangoproject.com/ticket/17966
# The new test runner in Django 1.5 will be more flexible:
#https://code.djangoproject.com/ticket/17365
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--detailed-errors',
    '--nologcapture',
]

SOUTH_TESTS_MIGRATE = False

SKIP_BB_FUNCTIONAL_TESTS = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        },
}
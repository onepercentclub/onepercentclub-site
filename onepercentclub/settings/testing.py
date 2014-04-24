#
# NOTE: This is the settings file for the server at https://testing.onepercentclub.com
#       This is not for running tests!
#

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
)

COWRY_RETURN_URL_BASE = 'https://testing.onepercentclub.com'
COWRY_LIVE_PAYMENTS = False

# Send email for real
EMAIL_BACKEND = 'bluebottle.utils.email_backend.TestMailBackend'

SESSION_COOKIE_NAME = 'bb-testing-session-id'

SOUTH_TESTS_MIGRATE = False
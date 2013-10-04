try:
    from .secrets import *
except ImportError:
    import sys
    sys.exit('secrets.py settings file not found. Please run `prepare.sh` to create one.')

from .base import *

#
# Put staging server environment specific overrides below.
#

DEBUG = False
TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS += (
    'gunicorn',
)

COWRY_RETURN_URL_BASE = 'https://staging.onepercentclub.com'
COWRY_LIVE_PAYMENTS = False

# Send email for real
EMAIL_BACKEND = 'bluebottle.bluebottle_utils.email_backend.DKIMBackend'

SESSION_COOKIE_NAME = 'bb-staging-session-id'

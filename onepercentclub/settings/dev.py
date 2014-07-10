try:
    from .secrets import *
except ImportError:
    import sys
    sys.exit('secrets.py settings file not found. Please run `prepare.sh` to create one.')

from .server import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

# Put dev server environment specific overrides below.

COWRY_RETURN_URL_BASE = 'https://dev.onepercentclub.com'
COWRY_LIVE_PAYMENTS = False

SESSION_COOKIE_NAME = 'bb-dev-session-id'

EMAIL_BACKEND = 'bluebottle.utils.email_backend.TestMailBackend'
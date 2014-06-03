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

SENTRY_DSN = 'https://6ab2de49f45e4aa3bb93be15854417b2@app.getsentry.com/24876'

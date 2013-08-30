try:
    from .secrets import *
except ImportError:
    import sys
    sys.exit('secrets.py settings file not found. Please run `prepare.sh` to create one.')

from .base import *

# Put dev server environment specific overrides below.

INSTALLED_APPS += (
    'gunicorn',
)

COWRY_RETURN_URL_BASE = 'https://dev.onepercentclub.com'
COWRY_LIVE_PAYMENTS = False

SESSION_COOKIE_NAME = 'bb-dev-session-id'

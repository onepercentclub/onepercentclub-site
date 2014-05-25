try:
    from .secrets import *
except ImportError:
    import sys
    sys.exit('secrets.py settings file not found. Please run `prepare.sh` to create one.')

from .server import *

#
# Put production server environment specific overrides below.
#

COWRY_RETURN_URL_BASE = 'https://onepercentclub.com'
COWRY_LIVE_PAYMENTS = True

# Send email for real
EMAIL_BACKEND = 'bluebottle.utils.email_backend.DKIMBackend'

SESSION_COOKIE_DOMAIN = '.onepercentclub.com'

ANALYTICS_CODE = 'UA-2761714-4'

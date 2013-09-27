try:
    from .secrets import *
except ImportError:
    import sys
    sys.exit('secrets.py settings file not found. Please run `prepare.sh` to create one.')

from .base import *


#
# We need this specific override because having the salesforce app and bluebottle_salesforce
# enabled causes tests to fail in our other apps with this error:
#
#    AttributeError: _original_allowed_hosts
#
# There seems to be some strange database interactions / side-effects when running with SaleforceModels that have
# Meta: managed = False set with the salesforce info configured in DATABASES.
# TODO: Investigate this issue to see if we can put the Saleforce apps back into base.py.
#

#
# Put the salesforce sync environment specific overrides below.
#

DEBUG = False
TEMPLATE_DEBUG = False

INSTALLED_APPS += (
    'salesforce',
    'apps.bluebottle_salesforce',
)

# Send email for real
EMAIL_BACKEND = 'apps.bluebottle_utils.email_backend.DKIMBackend'

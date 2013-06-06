try:
    from .secrets import *
except ImportError:
    import sys
    sys.exit('secrets.py settings file not found. Please run `prepare.sh` to create one.')

from .base import *

#
# Put testing environment specific overrides below.
#

DEBUG = False
TEMPLATE_DEBUG = False

INSTALLED_APPS += (
    'gunicorn',
)

COWRY_RETURN_URL_BASE = 'https://testing.onepercentclub.com'


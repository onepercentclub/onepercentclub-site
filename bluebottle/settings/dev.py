try:
    from .secrets import *
except ImportError:
    import sys
    sys.exit('secrets.py settings file not found. Please run `prepare.sh` to create one.')

from .base import *

# Put dev server environment specific overrides below.

COWRY_RETURN_URL_BASE = 'https://dev.onepercentclub.com'
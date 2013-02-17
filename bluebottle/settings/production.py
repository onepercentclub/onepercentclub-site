# NOTE: local.py must be an empty file when using this configuration.

try:
    from .secrets import *
except ImportError:
    import sys
    sys.exit('secrets.py settings file not found. Please run `prepare.sh` to create one.')

from .defaults import *

# Put production server environment specific overrides below.

DEBUG = False
TEMPLATE_DEBUG = False

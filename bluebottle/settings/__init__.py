# Smarter settings working, based on work by Rob Golding
# http://www.robgolding.com/blog/2010/05/03/extending-settings-variables-with-local_settings-py-in-django/

import sys

try:
    from .local import *
except ImportError:
    # Throw a return value of 1 and exit with a SystemExit exception
    # Ref: http://docs.python.org/library/sys.html#sys.exit
    sys.exit('Local settings file not found. Please run `prepare.sh` to create one.')

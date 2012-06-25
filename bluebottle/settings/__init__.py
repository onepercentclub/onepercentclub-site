# Smarter settings working, based on work by Rob Golding
# http://www.robgolding.com/blog/2010/05/03/extending-settings-variables-with-local_settings-py-in-django/

try:
    from .local import *
except ImportError:
    print 'Local settings file not found. Please run `prepare.sh` to create one.'

    exit(-1)

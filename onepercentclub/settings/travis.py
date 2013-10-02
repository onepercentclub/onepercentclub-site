
# SECRET_KEY and DATABASES needs to be defined before the base settings is imported.
SECRET_KEY = 'hbqnTEq+m7Tk61bvRV/TLANr3i0WZ6hgBXDh3aYpSU8m+E1iCtlU3Q=='

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

from .base import *

#
# Put the travis-ci environment specific overrides below.
#

# Disable Selenium testing for now on Travis because it fails inconsistent.
SELENIUM_TESTS = False
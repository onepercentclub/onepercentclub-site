# Import default settings

from .defaults import *

# Import secrets
from .secrets import *

# Put your environment specific overrides below

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'onepercentsite_migration',
        'USER': 'jenkins'
    },
    'legacy': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'legacy',
        'USER': 'jenkins'
    }
}

# Do not run legacy migrations in debugger on testing server
LEGACY_MIGRATIONS_DEBUG = False

# Turn off debugging for added speed and (hopefully) less memory usage
DEBUG = False

# On the devserver we expect static assets to live here
LEGACY_MIGRATIONS_MEDIA_ROOT = '/home/onepercent/data/live'

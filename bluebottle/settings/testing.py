# Settings for use on testing server
from .local import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'onepercentsite',
        'USER': 'jenkins'
    },
    'legacy': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'legacy',
        'USER': 'jenkins'
    }
}

# Do not run legacy migrations in debugger on testing server
DEBUG_LEGACY_MIGRATIONS = False

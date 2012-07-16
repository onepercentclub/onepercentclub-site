# Settings for use on testing server
from .local import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'onepercentsite',
    },
    'legacy': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'legacy',
    }
}

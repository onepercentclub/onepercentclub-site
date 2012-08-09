# Settings for use on testing server
from .testing import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'onepercentsite',
        'USER': 'onepercentsite'
    },
}

INSTALLED_APPS.append('gunicorn')

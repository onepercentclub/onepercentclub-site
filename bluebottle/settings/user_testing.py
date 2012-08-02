# Settings for use on testing server
from .testing import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bluebottle_user_testing',
        'USER': 'bluebottle'
    },
}

INSTALLED_APPS.append('gunicorn')


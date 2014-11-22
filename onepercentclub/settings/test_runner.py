#
# Note: Some standard settings for running tests - jenkins, travis or local
#
# TODO: Use this with the Jenkins settings file
#




SECRET_KEY = 'hbqnTEq+m7Tk61bvRV/TLANr3i0WZ6hgBXDh3aYpSU8m+E1iCtlU3Q=='
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

from .base import *


# Supress naive date warnings
import warnings
warnings.filterwarnings(
        'ignore', r"DateTimeField received a naive datetime .* while time zone support is active",
        RuntimeWarning, r'django\.db\.models\.fields')

DEBUG = False
TEMPLATE_DEBUG = False
COMPRESS_TEMPLATES = True

COMPRESS_PRECOMPILERS = (
    ('text/x-handlebars', 'embercompressorcompiler.filter.EmberHandlebarsCompiler'),
)

TEMPLATE_LOADERS = [
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
        'apptemplates.Loader', # extend AND override templates
    )),
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

# Selenium settings
SELENIUM_TESTS = True
SELENIUM_WEBDRIVER = 'chrome'
SOUTH_TESTS_MIGRATE = False

INSTALLED_APPS += (
    'django_nose',
    'bluebottle.payments_mock'
)

from bluebottle.payments_mock.settings import MOCK_PAYMENT_METHODS, MOCK_FEES

#Override the payment methods that are in payments.py in the settings directory
PAYMENT_METHODS = MOCK_PAYMENT_METHODS
VAT_RATE = 0.21
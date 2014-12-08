#
# Note: Some standard settings for running tests - jenkins, travis or local
#
# TODO: Use this with the Jenkins settings file
#

SECRET_KEY = 'hbqnTEq+m7Tk61bvRV/TLANr3i0WZ6hgBXDh3aYpSU8m+E1iCtlU3Q=='

from .base import *
from .templates import *

# Supress naive date warnings
import warnings
warnings.filterwarnings(
        'ignore', r"DateTimeField received a naive datetime .* while time zone support is active",
        RuntimeWarning, r'django\.db\.models\.fields')

DEBUG = False
TEMPLATE_DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

# Selenium settings
SELENIUM_TESTS = True
SELENIUM_WEBDRIVER = 'chrome'
SOUTH_TESTS_MIGRATE = False

INSTALLED_APPS += (
    'django_nose',
    'bluebottle.payments_mock'
)

#Override the payment methods that are in payments.py in the settings directory
from bluebottle.payments_mock.settings import MOCK_PAYMENT_METHODS, MOCK_FEES
PAYMENT_METHODS = MOCK_PAYMENT_METHODS
VAT_RATE = 0.21

from .base import *
from .templates import *

DEBUG = False
TEMPLATE_DEBUG = False

INSTALLED_APPS += (
    'gunicorn',
)
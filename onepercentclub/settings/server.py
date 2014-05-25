try:
    from .secrets import *
except ImportError:
    import sys
    sys.exit('secrets.py settings file not found. Please run `prepare.sh` to create one.')

from .base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS += (
    'gunicorn',
)

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

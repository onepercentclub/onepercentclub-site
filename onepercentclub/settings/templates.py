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
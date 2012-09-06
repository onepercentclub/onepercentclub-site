# Django settings for bluebottle project.

# Import global settings for overriding without throwing away defaults
from django.conf import global_settings

from os import path

# Set PROJECT_ROOT to the dir of the current file
# Find the project's containing directory and normalize it to refer to
# the project's root more easily
PROJECT_ROOT = path.dirname(path.normpath(path.join(__file__, '..', '..')))

# DJANGO_PROJECT: the short project name
# (defaults to the basename of PROJECT_ROOT)
DJANGO_PROJECT = path.basename(PROJECT_ROOT.rstrip('/'))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Amsterdam'


"""
Available user interface translations
Ref: https://docs.djangoproject.com/en/1.4/ref/settings/#languages
"""
# Default language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# This is defined here as a do-nothing function because we can't import
# django.utils.translation -- that module depends on the settings.
gettext_noop = lambda s: s

LANGUAGES = (
    ('nl', gettext_noop('Dutch')),
    ('en', gettext_noop('English'))
)


SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
# pytz is in requirements.txt because it's "highly recommended" when using
# timezone support.
# https://docs.djangoproject.com/en/1.4/topics/i18n/timezones/
USE_TZ = True

"""
staticfiles and media

For staticfiles and media, the following convention is used:

* '/static/media/': Application media default path
* '/static/global/': Global static media
* '/static/apps/<app_name>/': Static assets after running `collectstatic`

The respective URL's (available only when `DEBUG=True`) are in `urls.py`.

More information:
https://docs.djangoproject.com/en/1.4/ref/contrib/staticfiles/
"""

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = path.join(PROJECT_ROOT, 'static', 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/static/media/'



# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = path.join(PROJECT_ROOT, 'static', 'assets')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/assets/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    ('global', path.join(PROJECT_ROOT, 'static', 'global')),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
]

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
]

"""
These are basically the default values from the Django configuration, written
as a list for easy manipulation. This way one can:

1. Easily add, remove or replace elements in the list, ie. overriding.
2. Know what the defaults are, if you want to change them right here. This
   way you won't have to look them up everytime you want to change.
"""
MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # https://docs.djangoproject.com/en/1.4/ref/clickjacking/
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Browsers will block our pages from loading in an iframe no matter which site
# made the request. This setting can be overridden on a per response or a per
# view basis with the @xframe decorators.
X_FRAME_OPTIONS = 'DENY'

TEMPLATE_CONTEXT_PROCESSORS = [
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.static',
    # 'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    # Makes the 'request' variable (the current HttpRequest)
    # available in templates
    'django.core.context_processors.request',
    'gitrevision.context_processors.gitrevision',
]

ROOT_URLCONF = 'bluebottle.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'bluebottle.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    path.join(PROJECT_ROOT, 'templates')
)

INSTALLED_APPS = [
    # Django apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',

    # 3rd party apps
    'django_extensions',
    'django_extensions.tests',
    'debug_toolbar',
    'raven.contrib.django',
    'djcelery',
    'south',
    'django_nose',
    'compressor',
    'sorl.thumbnail',
    'taggit',
    'micawber.contrib.mcdjango', # Embedding videos
    'gitrevision', # Display git revision
    'templatetag_handlebars',

    # bluebottle apps
    'apps.bluebottle_utils',
    'apps.accounts',
    'apps.organizations',
    'apps.projects',
    'apps.donations',
    'apps.media',
    'apps.geo',
]

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


""" djcelery """
import djcelery
djcelery.setup_loader()


""" django-nose """
# Nose is temporarily not the default testrunner due to
# https://github.com/jbalogh/django-nose/issues/85
# TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
# NOSE_ARGS = [
#     '--detailed-errors',
# ]

SOUTH_TESTS_MIGRATE = False # Make south shut up during tests


""" django-compressor http://pypi.python.org/pypi/django_compressor """
STATICFILES_FINDERS += [
    # django-compressor staticfiles
    'compressor.finders.CompressorFinder',
]

# Enable by default
COMPRESS_ENABLED = True
COMPRESS_OUTPUT_DIR = 'compressed'

COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    #'compressor.filters.datauri.DataUriFilter',
    'compressor.filters.cssmin.CSSMinFilter'
]

# Automagic CSS precompilation
#COMPRESS_PRECOMPILERS = (
#    ('text/coffeescript', 'coffee --compile --stdio'),
#    ('text/less', 'lessc {infile} {outfile}'),
#    ('text/x-sass', 'sass {infile} {outfile}'),
#    ('text/x-scss', 'sass --scss {infile} {outfile}'),
#)

# The default URL to send users to after login. This will be used when the
# 'next' URL parameter hasn't been set.
LOGIN_REDIRECT_URL = '/'

# user profile setting as described here:
# https://docs.djangoproject.com/en/1.4/topics/auth/#storing-additional-information-about-users
AUTH_PROFILE_MODULE = 'accounts.UserProfile'


# Required for handlebars_template to work properly
USE_EMBER_STYLE_ATTRS = True

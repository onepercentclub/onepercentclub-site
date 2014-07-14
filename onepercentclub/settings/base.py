# coding=utf-8
# Django settings for bluebottle project.

import os, datetime

# Import global settings for overriding without throwing away defaults
from django.conf import global_settings
from django.utils.translation import ugettext as _
from admin_dashboard import *

# Set PROJECT_ROOT to the dir of the current file
# Find the project's containing directory and normalize it to refer to
# the project's root more easily
PROJECT_ROOT = os.path.dirname(os.path.normpath(os.path.join(__file__, '..', '..')))

# DJANGO_PROJECT: the short project name
# (defaults to the basename of PROJECT_ROOT)
DJANGO_PROJECT = os.path.basename(PROJECT_ROOT.rstrip('/'))

DEBUG = True
TEST_MEMCACHE = False
TEMPLATE_DEBUG = True
COMPRESS_TEMPLATES = False

ADMINS = (
    ('Loek van Gent', 'loek@1procentclub.nl'),
)

CONTACT_EMAIL = 'info@onepercentclub.com'

MANAGERS = ADMINS

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['.onepercentclub.com', '.1procentclub.nl']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Amsterdam'


# Available user interface translations
# Ref: https://docs.djangoproject.com/en/1.4/ref/settings/#languages
#
# Default language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

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

# First one is for apps the second for the main templates
LOCALE_PATHS = ('../locale', 'locale')

# If you set this to False, Django will not use timezone-aware datetimes.
# pytz is in requirements.txt because it's "highly recommended" when using
# timezone support.
# https://docs.djangoproject.com/en/1.4/topics/i18n/timezones/
USE_TZ = True


# Static Files and Media
# ======================
#
# For staticfiles and media, the following convention is used:
#
# * '/static/media/': Application media default path
# * '/static/global/': Global static media
# * '/static/assets/<app_name>/': Static assets after running `collectstatic`
#
# The respective URL's (available only when `DEBUG=True`) are in `urls.py`.
#
# More information:
# https://docs.djangoproject.com/en/1.4/ref/contrib/staticfiles/

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'static', 'media')

# Absolute filesystem path to the directory that will hold PRIVATE user-uploaded files.
PRIVATE_MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'private', 'media')


# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/static/media/'
PRIVATE_MEDIA_URL = '/private/media/'


# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static', 'assets')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/assets/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # You can also name this tuple like: ('css', '/path/to/css')
    (os.path.join(PROJECT_ROOT, 'static', 'global')),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
]

TEMPLATE_LOADERS = [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'apptemplates.Loader', # extend AND override templates
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# These are basically the default values from the Django configuration, written
# as a list for easy manipulation. This way one can:
#
# 1. Easily add, remove or replace elements in the list, ie. overriding.
# 2. Know what the defaults are, if you want to change them right here. This
#   way you won't have to look them up every time you want to change.
#
# Note: The first three middleware classes need to be in this order: Session, Locale, Common
# http://stackoverflow.com/questions/8092695/404-on-requests-without-trailing-slash-to-i18n-urls
MIDDLEWARE_CLASSES = [
    'bluebottle.auth.middleware.UserJwtTokenMiddleware',
    'apps.redirects.middleware.RedirectHashCompatMiddleware',
    'bluebottle.auth.middleware.AdminOnlyCsrf',
    # Have a middleware to make sure old cookies still work after we switch to domain-wide cookies.
    'bluebottle.utils.middleware.SubDomainSessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'bluebottle.auth.middleware.AdminOnlySessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'bluebottle.auth.middleware.AdminOnlyAuthenticationMiddleware',
    'bluebottle.bb_accounts.middleware.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # https://docs.djangoproject.com/en/1.4/ref/clickjacking/
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'apps.redirects.middleware.RedirectFallbackMiddleware',
    'apps.crawlable.middleware.HashbangMiddleware',
    'django_tools.middlewares.ThreadLocal.ThreadLocalMiddleware',
    'bluebottle.auth.middleware.SlidingJwtTokenMiddleware'
]

# Browsers will block our pages from loading in an iframe no matter which site
# made the request. This setting can be overridden on a per response or a per
# view basis with the @xframe decorators.
X_FRAME_OPTIONS = 'DENY'


TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    # Makes the 'request' variable (the current HttpRequest) available in templates.
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
    'bluebottle.utils.context_processors.installed_apps_context_processor',
    'bluebottle.utils.context_processors.git_commit',
    'bluebottle.utils.context_processors.conf_settings',
    'bluebottle.utils.context_processors.google_maps_api_key',
    'bluebottle.utils.context_processors.google_analytics_code',
    'bluebottle.utils.context_processors.sentry_dsn',
    'bluebottle.utils.context_processors.facebook_auth_settings',
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
)

ROOT_URLCONF = 'onepercentclub.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'onepercentclub.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, 'templates')
)

INSTALLED_APPS = (
    # Django apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd party apps
    'django_extensions',
    'django_extensions.tests',
    'raven.contrib.django.raven_compat',
    'djcelery',
    'south',
    # 'django_nose',
    'compressor',
    'sorl.thumbnail',
    'taggit',
    'taggit_autocomplete_modified',
    'micawber.contrib.mcdjango',  # Embedding videos
    'templatetag_handlebars',
    'rest_framework',
    'rest_framework.authtoken',
    'polymorphic',
    'registration',
    'filetransfers',
    'loginas',
    #'social_auth',
    'social.apps.django_app.default',

    # CMS page contents
    'fluent_contents',
    'fluent_contents.plugins.text',
    'fluent_contents.plugins.oembeditem',
    'fluent_contents.plugins.rawhtml',
    'django_wysiwyg',
    'tinymce',
    'statici18n',
    'django.contrib.humanize',
    'django_tools',

    #FB Auth
    'bluebottle.auth',

    # Cowry Payments
    'apps.cowry',
    'apps.cowry_docdata',
    'apps.cowry_docdata_legacy',

    # Password auth from old PHP site.
    'legacyauth',

    'apps.vouchers',
    'apps.fund',
    'apps.fundraisers',
    'bluebottle.wallposts', # Define wall posts before projects/tasks that depend on it.
    'apps.donations',

    # Apps extending Bluebottle base models
    'apps.members',
    'apps.tasks',
    'apps.projects',
    'apps.organizations',

    # apps overriding bluebottle functionality should come before the bluebottle entries
    # (template loaders pick the first template they find)
    'apps.core',

    # Other Bluebottle apps
    'bluebottle.utils',
    'bluebottle.common',
    'bluebottle.contentplugins',
    'bluebottle.contact',
    'bluebottle.geo',
    'bluebottle.pages',
    'bluebottle.news',
    'bluebottle.slides',
    'bluebottle.quotes',

    # Bluebottle apps with abstract models
    'bluebottle.bb_accounts',
    'bluebottle.bb_organizations',
    'bluebottle.bb_projects',
    'bluebottle.bb_tasks',

    'apps.bluebottle_salesforce',

    'apps.bluebottle_dashboard',
    'apps.contentplugins',
    'apps.campaigns',
    'apps.hbtemplates',
    'apps.payouts',
    'apps.sepa',
    'apps.statistics',
    'apps.homepage',
    'apps.redirects',
    'apps.partners',
    'apps.csvimport',
    'apps.accounting',
    'apps.crawlable',

    # Custom dashboard
    'fluent_dashboard',
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    'django.contrib.admin',
    'django.contrib.admindocs',
)

# Custom User model
AUTH_USER_MODEL = 'members.Member'
PROJECTS_PROJECT_MODEL = 'projects.Project'
PROJECTS_PHASELOG_MODEL = 'projects.ProjectPhaseLog'
TASKS_TASK_MODEL = 'tasks.Task'
TASKS_SKILL_MODEL = 'tasks.Skill'
TASKS_TASKMEMBER_MODEL = 'tasks.TaskMember'
TASKS_TASKFILE_MODEL = 'tasks.TaskFile'
ORGANIZATIONS_ORGANIZATION_MODEL = 'organizations.Organization'
ORGANIZATIONS_DOCUMENT_MODEL = 'organizations.OrganizationDocument'
ORGANIZATIONS_MEMBER_MODEL = 'organizations.OrganizationMember'
PROJECTS_PHASELOG_MODEL = 'projects.ProjectPhaseLog'

SOCIAL_AUTH_USER_MODEL = 'members.Member'
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', 'user_friends', 'public_profile', 'user_birthday']
SOCIAL_AUTH_FACEBOOK_EXTRA_DATA = [('birthday', 'birthday')]

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
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
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'bluebottle.salesforce': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'cowry.docdata': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# log errors & warnings
import logging
logging.basicConfig(level=logging.WARNING, format='[%(asctime)s] %(levelname)-8s %(message)s', datefmt="%d/%b/%Y %H:%M:%S")


# Django Celery - asynchronous task server
import djcelery
djcelery.setup_loader()

SOCIAL_AUTH_STRATEGY = 'social.strategies.django_strategy.DjangoStrategy'
SOCIAL_AUTH_STORAGE = 'social.apps.django_app.default.models.DjangoStorage'

AUTHENTICATION_BACKENDS = (
    'social.backends.facebook.FacebookAppOAuth2',
    'social.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# We're using nose because it limits the tests to our apps (i.e. no Django and
# 3rd party app tests). We need this because tests in contrib.auth.user are
# failing in Django 1.4.1. Here's the ticket for the failing test:
# https://code.djangoproject.com/ticket/17966
# The new test runner in Django 1.5 will be more flexible:
#https://code.djangoproject.com/ticket/17365
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--detailed-errors',
    '--nologcapture',
]

SKIP_BB_FUNCTIONAL_TESTS = True


SOUTH_TESTS_MIGRATE = False  # Make south shut up during tests


# django-compressor http://pypi.python.org/pypi/django_compressor
# Compressor is enabled whenever DEBUG is False.
STATICFILES_FINDERS += [
    # django-compressor staticfiles
    'compressor.finders.CompressorFinder',
]

# TODO Enable compass here.
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


# Blog/news content configuration
FLUENT_CONTENTS_CACHE_OUTPUT = True
FLUENT_TEXT_CLEAN_HTML = True
FLUENT_TEXT_SANITIZE_HTML = True
DJANGO_WYSIWYG_FLAVOR = 'tinymce_advanced'


# Required for handlebars_template to work properly
USE_EMBER_STYLE_ATTRS = True

# Sorl Thumbnail settings
# http://sorl-thumbnail.readthedocs.org/en/latest/reference/settings.html
THUMBNAIL_QUALITY = 85
# TODO: Configure Sorl with Redis.

REST_FRAMEWORK = {
    'FILTER_BACKEND': 'rest_framework.filters.DjangoFilterBackend',
    # Don't do basic authentication.
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=7),
    'JWT_LEEWAY': 0,
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,

    'JWT_ALLOW_TOKEN_RENEWAL': True,
    # After the renewal limit it isn't possible to request a token refresh
    # => time token first created + renewal limit.
    'JWT_TOKEN_RENEWAL_LIMIT': datetime.timedelta(days=90),
}
# Time between attempts to refresh the jwt token automatically on standard request
# TODO: move this setting into the JWT_AUTH settings.
JWT_TOKEN_RENEWAL_DELTA = datetime.timedelta(minutes=30)

COWRY_RETURN_URL_BASE = 'http://127.0.0.1:8000'

COWRY_PAYMENT_METHODS = {
    'dd-webmenu': {
        'profile': 'webmenu',
        'name': 'DocData Web Menu',
        'supports_recurring': False,
        'supports_single': True,
    },

    'dd-webdirect': {
        'profile': 'webdirect',
        'name': 'DocData WebDirect Direct Debit',
        'restricted_countries': ('NL',),
        'supports_recurring': True,
        'supports_single': False,
    },
}

# Default VAT percentage as string (used in payouts)
VAT_RATE = '0.21'

# Settings for organization bank account. Please set this in secrets.py
# SEPA = {
#     'iban': '',
#     'bic': '',
#     'name': '',
#     'id': ''
# }

# Salesforce app settings
SALESFORCE_QUERY_TIMEOUT = 3
DATABASE_ROUTERS = [
    "salesforce.router.ModelRouter"
]

# E-mail settings
DEFAULT_FROM_EMAIL = '<website@onepercentclub.com> 1%Club'


# Django-registration settings
ACCOUNT_ACTIVATION_DAYS = 4
HTML_ACTIVATION_EMAIL = True  # Note this setting is from our forked version.

# Functional testing
# Selenium and Splinter settings
SELENIUM_TESTS = True
SELENIUM_WEBDRIVER = 'phantomjs'  # Can be any of chrome, firefox, phantomjs

FIXTURE_DIRS = [
    os.path.join(DJANGO_PROJECT, 'fixtures')
]

# PhantomJS for flat page generation.
# NOTE: This has nothing to do with testing against phantomjs.
CRAWLABLE_PHANTOMJS_DEDICATED_MODE = True
# If dedicated mode is enabled, configure the port:
CRAWLABLE_PHANTOMJS_DEDICATED_PORT = 8910
# If dedicated mode is disabled, you can specify arguments to start phantomjs.
CRAWLABLE_PHANTOMJS_ARGS = []
# Use HTTPS for PhantomJS requests.
CRAWLABLE_FORCE_HTTPS = True

# Send email to console by default
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

STATICI18N_ROOT = os.path.join(PROJECT_ROOT, 'static', 'global')

SESSION_COOKIE_NAME = 'bb-session-id'

# Support legacy passwords
PASSWORD_HASHERS = global_settings.PASSWORD_HASHERS + (
    'legacyauth.hashers.LegacyPasswordHasher',
)

# Twitter handles, per language
TWITTER_HANDLES = {
    'nl': '1procentclub',
    'en': '1percentclub',
}
DEFAULT_TWITTER_HANDLE = TWITTER_HANDLES['nl']

MINIMAL_PAYOUT_AMOUNT = 21.00
SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.social_auth.associate_by_email',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
    'bluebottle.auth.utils.save_profile_picture',
    'bluebottle.auth.utils.get_extra_facebook_data',
    'bluebottle.auth.utils.send_welcome_mail_pipe'
)

SOCIAL_AUTH_PROTECTED_USER_FIELDS = ['email', 'first_name', 'last_name', ]
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True

SEND_WELCOME_MAIL = True

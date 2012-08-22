from django.conf import settings


MIGRATIONS = settings.LEGACY_MIGRATIONS

DEBUG_MIGRATIONS = getattr(settings, 'LEGACY_MIGRATIONS_DEBUG', True)
LEGACY_MEDIA_ROOT = settings.LEGACY_MIGRATIONS_MEDIA_ROOT

# Whether or not to enable exclusions for dirty data , defaults to False
ENABLE_EXCLUSIONS = getattr(
    settings,
    'LEGACY_MIGRATIONS_ENABLE_EXCLUSIONS',
    False
)

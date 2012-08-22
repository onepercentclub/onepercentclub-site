import time

from django.core.exceptions import ImproperlyConfigured
from django.utils.datastructures import SortedDict
from django.utils.functional import memoize
from django.utils.importlib import import_module


class Timer:
    """
    Generic timer class.

    Source:
    http://preshing.com/20110924/timing-your-code-using-pythons-with-statement
    """
    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start


_migrations = SortedDict()

def _get_migration(import_path):
    """
    Imports the staticfiles migration class described by import_path, where
    import_path is the full Python path to the class.

    This code has been borrowed from Django's staticfiles contrib.
    """
    from .base import MigrateModel

    module, attr = import_path.rsplit('.', 1)
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing module %s: "%s"' %
                                   (module, e))
    try:
        Migration = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" '
                                   'class.' % (module, attr))
    if not issubclass(Migration, MigrateModel):
        raise ImproperlyConfigured('Migration "%s" is not a subclass of "%s"' %
                                   (Migration, MigrateModel))
    return Migration()
get_migration = memoize(_get_migration, _migrations, 1)

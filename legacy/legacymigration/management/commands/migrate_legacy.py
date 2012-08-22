import logging

from ipdb import launch_ipdb_on_exception

from django.core.management.base import BaseCommand

from ...settings import MIGRATIONS, DEBUG_MIGRATIONS
from ...utils import get_migration


class Command(BaseCommand):
    help = 'Migrate existing legacy models.'
    can_import_settings = True
    requires_model_validation = True

    """
    Map verbosity to log levels, according to: (from Django manual)

    0 means no output.
    1 means normal output (default).
    2 means verbose output.
    3 means very verbose output.
    """
    verbosity_loglevel = {
        '0': logging.ERROR,
        '1': logging.WARNING,
        '2': logging.INFO,
        '3': logging.DEBUG
    }

    def _run_migration(self, migration):
        """ Run a single migration. """

        migration_instance = get_migration(migration)
        migration_instance.migrate_all()

    def _run_migrations(self, *args):
        """ Run a series of migrations. """

        for migration in MIGRATIONS:
            # Execute all migrations, unless a set of migration classes
            # have been specified on the command line
            if not args or migration.rsplit('.', 1)[1] in args:
                self._run_migration(migration)

    def handle(self, *args, **options):
        # Setup the log level for root logger
        loglevel = self.verbosity_loglevel.get(options['verbosity'])
        logging.getLogger().setLevel(loglevel)

        # When debugging, launch ipdb on exception
        if DEBUG_MIGRATIONS:
            # Exception launches ipdb https://github.com/Psycojoker/ipdb#use
            with launch_ipdb_on_exception():
                self._run_migrations(*args)
        else:
            # Just run the migrations
            self._run_migrations(*args)

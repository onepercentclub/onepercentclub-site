Legacy migration
================

.. currentmodule:: legacy.legacymigration

`legacymigration` App Overview
-------------------------------
Migrations are executed from the `legacymigration` app. Within the app, a base module called  `MigrateModel` defines a generic correspondence-based migration strategy from one model instance in one database to a model instance in another database.

Actual migrations are performed by subclassing the `MigrateModel` class, defining (at the very least) the `from_model`, `to_model` and `field_mapping` attributes. Also, the `from_db` and `to_db` attributes can be specified, which default to migrating from database `legacy` to `default`.

After having defined a migration class, the particular migration can be
activated by adding it to the `LEGACY_MIGRATIONS` configuration option, which
should be a list. The migrations in this list can be performed by running
the :ref:`management-command`.

.. _field-mappings:

Field mappings
**************
Field mappings from the old model to the new model, as executed by the `copy_fields` method, can be specified in three
different ways:

1. A value of `True` for the mapping means the field will be copied as-is to the new model.
2. A string value causes the legacy field to be mapped to the new field with the string as name.
3. A function with signature `f(instance, fieldname) -> dict` will cause all of the values returned by the function to be set on the destination model.

.. _file-structure:

File structure
***************
The app is structured as follows:

* `base.py`: `MigrateModel` base class.
* `mappings.py`: `Mappings` classes for mapping legacy to new fields and checking whether the mapping went right.
* `settings.py`: Migration specific change settings.
* `utils.py`: Misc. helper utils.
* `<app_domain>.py`: Migrations of specific logical domains.

.. _settings:

Settings
********

* `LEGACY_MIGRATIONS`: Iterable of strings referring to migration classes to execute.
* `LEGACY_MIGRATIONS_DEBUG`: Trigger `ipdb <https://github.com/gotcha/ipdb>`_ on exceptions during migration. Defaults to `True`.
* `LEGACY_MIGRATIONS_MEDIA_ROOT`: Root path for file migrations.

.. _migration-workflow:

Migration workflow
--------------------

The general workflow for running migrations is as follows:

#. Configure the :ref:`database-structure` and load the `legacy` data.
#. Create Django models for the existing data using `inspectdb <https://docs.djangoproject.com/en/dev/howto/legacy-databases/#auto-generate-the-models>`_.
#. Configure migration :ref:`settings`.
#. Create :class:`MigrationModel` subclasses for the legacy models you want to migrate.
#. Run the :ref:`management-command`.

.. _database-structure:

Database structure
******************
The general process of executing a migration is to load the existing SQL into a database defined as `legacy`, which migrates all the data over to a pristine and fully separated `default` database.

In the Django settings, these databases can be defined as follows::

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': '<new_database>',
            'USER': '<db_user>',
        },

        'legacy': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': '<legacy_database>',
            'USER': '<db_user>',
        }
    }

Given a clean setup and a Postgres database dump in Gzipped SQL, the steps required to load the legacy database are as follows::

    sudo -u postgres createdb -T template0 -E utf8 <legacy_database>
    gunzip -c <gzipped_sql_dump>.sql.gz | sudo -u postgres psql <legacy_database>

After this we can initialize the new database in the ordinary way::

    sudo -u postgres createdb -T template0 -E utf8 <new_database>
    ./manage.py syncdb --migrate

These steps are only needed once, after which legacy migrations can be maintained using the `legacy_migrate` command.

.. _management-command:

`migrate_legacy` Django management command
*******************************************
A series of migrations can be scripted through the `migrate_legacy` command, defined in `legacymigration/management/commands/migrate_legacy.py`. This command allows for easy specification of verbosity level (logging) using the `--verbosity {0,1,2,3}` argument and will run all migrations such that exceptions will throw you straight into an interactive debugger.

The `migrate_legacy` command can be executed as such::

    ./manage.py migrate_legacy -v 2
    [05/Jul/2012 11:19:10] INFO     50 objects migrated
    [05/Jul/2012 11:19:10] INFO     100 objects migrated
    [05/Jul/2012 11:19:10] INFO     150 objects migrated
    [05/Jul/2012 11:19:11] INFO     200 objects migrated
    [05/Jul/2012 11:19:11] INFO     250 objects migrated
    [05/Jul/2012 11:19:11] INFO     300 objects migrated
    [05/Jul/2012 11:19:12] WARNING  Field value '<some_value>' for '<Member: 457: somevalue>' too long, cropping to 30 characters.
    ...

Alternately, only a limited number of migrations can be executed by specifying their class names as parameters to the `migrate_legacy` command::

    ./manage.py migrate_legacy -v 2 MigrateProfile MigrateUserAddress

These migrations will be executed in the order in which they have been specified in `LEGACY_MIGRATIONS`.

Auto-generated documentation
----------------------------

Migration base class
****************************************************

.. automodule:: legacy.legacymigration.base
    :members:

Mappings
********

.. automodule:: legacy.legacymigration.mappings
    :members:

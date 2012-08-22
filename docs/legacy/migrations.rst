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
Field mappings from the old model to the new model, as executed by the :meth:`~base.MigrateModel.map_fields` method, can be specified in several
different ways:

1. A value of `True` for the mapping means the field will be copied as-is to the new model.
2. A value of `None` for explicitly throwing away a particular field (rather than having the migration script emit warnings for unmigrated data).
3. A string value to specify the field name to map the current value to.
4. Instances of subclasses from :class:`Mapping`, performing field-specific operations like the :class:`CroppingMapping`, :class:`SlugifyMapping`.
5. A dictionary to map field values of a related objects, for example::

        field_mappings = {
            'user': {
                'profile': <Mapping>
            }
        }

   The specified `<Mapping>` is an ordinary field mapping and can be specified
   as such.

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
* `LEGACY_MIGRATIONS_MEDIA_ROOT`: Root path for :ref:`files that are to be migrated <migrating-files>` along with the models.
* `LEGACY_MIGRATIONS_ENABLE_EXCLUSIONS`: Whether or not :ref:`exclusions` are enabled. Defaults to `False`.

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

These steps are only needed once, after which legacy migrations can be maintained using the :ref:`management-command`.

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

Additional features
-------------------

.. _exclusions:

Exclusions for 'unclean' data
*****************************

Often, during legacy migrations, some data cannot easily be migrated to fit
into the new datastructure. Rather, it has to be updated manually in the
source dataset, which takes time and often depends on people other than the
ones performing the migrations.

In order allow for a non-blocking development of migrations, so that
migrations can be performed even with 'unclean' source data, the migration
mechanism provides a facility for explicitly excluding data from the source
queryset.

These exclusions can easily be toggled using a :ref:`Django setting <settings>`, so that whenever new data comes in it is simple to check whether
the state of the source data is 'clean' now.

Exclusions can be defined in the :py:meth:`~base.MigrateModel.list_from_exclusions` method on the migration instance.

.. _migrating-files:

Migrating of files
******************

During the migration of legacy data, we often need to migrate media from the
legacy models to the new application. This can be done by using the
:class:`~mappings.PathToFileMapping`, which maps string references
to source files to Django File objects.

As often the source files for the different source models are structured
differently from the new models, so the path to these files needs to be
specified explicitly as `root_path` when instantiating the
:class:`~mappings.PathToFileMapping`.

However, files are usually in subdirectories of a common root, for which the
setting :ref:`LEGACY_MIGRATIONS_MEDIA_ROOT <settings>` is used. This setting
should then be explicitly imported whenever files are migrated. An example::

    from .settings import LEGACY_MIGRATIONS_MEDIA_ROOT

    class MyFunkyMigration(MigrateModel):
        field_mapping = {
            'file':
                PathToFileMapping(
                    root_path=LEGACY_MEDIA_ROOT + '/assets/files/filemanager',
                    allow_missing=True,
                    to_field='picture',
                    verbose=False
                ),
        }


.. _logging:

Verbosity and Logging
*********************

Several messages are logged during the migrations, depending on the verbosity
level. Like all Django management commands, `migrate_legacy` takes a `-v`
option with a  verbosity value of `0`, `1` or `2`.

With the default value of `0`, only errors and warning are logged. A verbosity
value of `1` also logs info messages and a value of `2` logs debug messages.

The following information is logger for the respective log levels:

* `DEBUG`: Log every individual object that is being migrated or tested.
* `INFO`: Checkpointing, timing information and other general status updates.
* `WARNING`: Information that the user needs to be aware of, like fields that are not migrated, model validation errors and values that are changed during mappings (when `verbose=True`).
* `ERROR`: Messages about problems that will prohibit the migration from completing succesfully, like failures of integrity tests.

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

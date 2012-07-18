Legacy migration
================

`legacymigration` App Overview
-------------------------------
Migrations are governed from `legacymigration ` app. Within the app, a base module called  `MigrateModel` defines a generic correspondence-based migration strategy from one model in one database to another model in another database.

Actual migrations are performed by subclassing the `MigrateModel` class, defining the `from_model`, `to_model` and `field_mapping` attributes. Also, the `from_db` and `to_db` attributes can be specified, which default to migrating from database `legacy` to `default`. 

After having defined the class, we can instantiate the class and initiate a full migration by calling the `migrate_all` method on the class, like such::

        m = MigrateMemberAuth()
        m.migrate_all()

The `migrate_all` method will:

1. Get a QuerySet with all legacy objects to migrate.
2. Get the corresponding new object to migrate to using the `get_to` method, which in turn uses `get_correspondence_args` to define the conditions of the correspondence relation.
3. Call the `migrate_single` call for every object and saving the result.
4. After having migrated all the objects, run `test_multiple` on the QuerySet with legacy objects, which (by default) does bi-directional correspondence tests and calls `test_single` on every pair of migrated objects.
5. If `test_multiple` returns `True`, it will commit the changes to the database (all operations run within a single transaction).

Field mappings
**************
Field mappings from the old model to the new model, as executed by the `copy_fields` method, can be specified in three
different ways:

1. A value of `True` for the mapping means the field will be copied as-is to the new model.
2. A string value causes the legacy field to be mapped to the new field with the string as name.
3. A function with signature `f(instance, fieldname) -> dict` will cause all of the values returned by the function to be set on the destination model.

File structure
***************
The app is structured as follows:

* `base.py`: `MigrateModel` base class.
* `mappings.py`: `Mappings` classes for mapping legacy to new fields and checking whether the mapping went right.
* `settings.py`: Migration specific change settings.
* `utils.py`: Misc. helper utils.
* `<app_domain>.py`: Migrations of specific logical domains.

Settings
********

* `LEGACY_MIGRATIONS`: Iterable of strings referring to migration classes to execute.
* `LEGACY_MIGRATIONS_DEBUG`: Whether or not to bail out into ipdb when a migration fails. Defaults to `True`.
* `LEGACY_MIGRATIONS_MEDIA_ROOT`: Root path for file migrations.

Migration workflow
--------------------

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

Alternately, only a limited number of migrations can be executed by specifying their class names as parameters to the `migrate_legacy` command, ie.::

    ./manage.py migrate_legacy -v 2 MigrateProfile MigrateUserAddress

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

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

File structure
***************
The app is structured as follows:

* `base.py`: `MigrateModel` base class.
* `utils.py`: Generic util helper functions common to model migrations, such as `localize_datetime` for adding timezones and `crop_field` for cropping field values.
* `users.py`: Migration of authentication.
* `<app_domain>.py`: Migrate some other logical unit of the legacy application.

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
-------------------------------------------
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

Example migration and automated documentation
-------------------------------------------------

Example migration (users)
*************************

.. code-block:: python

    class MigrateMemberAuth(MigrateModel):
        """
        Migrate legacy members to Django users.
        """

        from_model = Member # Copy elements from one model to another
        to_model = User

        # This is the real cheese
        field_mapping = {
            'id': None, # None means just copy the field
            'email': None,

            'username': None,
            'profile': migrate_profile, # Execute a named function

            'password': lambda i, f: {'password': 'legacy$%s' % getattr(i, f)},
            # A function can be specified to yield a dictionary

            'created': lambda i, f: {'date_joined': localize_datetime(i, f)},
            'updated': lambda i, f: {'last_login': localize_datetime(i, f)},
            # A string can be passed to map to a different field
        }

        def test_single(self, from_instance, to_instance):
            """
            Test single items. Make sure to call the superclass.

            Return False and make sure to use logging when an error occurs.
            """

            success = super(MigrateMemberAuth, self).test_single(from_instance, to_instance)

            if from_instance.username != to_instance.username:
                logger.error('No correspondence in username between %s and %s',
                    repr(from_instance), repr(to_instance)
                )

                success = False

            if from_instance.email != to_instance.email:
                logger.error('No correspondence in email between %s and %s',
                    repr(from_instance), repr(to_instance)
                )

                success = False

            if from_instance.profile:
                profile = from_instance.profile

                if profile.firstname and \
                    profile.firstname[:30] != to_instance.first_name:

                    logger.error('No correspondence in first name between %s and %s',
                        repr(from_instance), repr(to_instance)
                    )

                    success = False

                if profile.lastname and \
                    from_instance.profile.lastname[:30] != to_instance.last_name:

                    logger.error('No correspondence in last name between %s and %s',
                        repr(from_instance), repr(to_instance)
                    )

                    success = False

            return success

        def test_multiple(self, from_qs):
            """
            Test multiple items. Returns False when error to prevent DB commit.

            Make sure to call the superclass here.
            """

            # First, call the method from the superclass
            success = super(MigrateMemberAuth, self).test_multiple(from_qs)

            # Now, test a bunch of users
            test_users = (
                ('usermigrationtest2', 'pohji8'), # Activated user
                ('mathijs@visualspace.nl', 'pohji8'), # Activated user usermigrationtest2
                ('glavangadje', 'ภาษาไทย'), # Thai, in Thai
                ('drbob@dokterbob.net', 'ภาษาไทย') # Previous user glavangadje
            )

            for user in test_users:
                if not authenticate(username=user[0], password=user[1]):
                    logger.error("Test user '%s' could not login with password '%s'",
                        user[0], user[1]
                    )
                    success = False

            return success


        def list_from(self):
            """
            Filter elements to sync
            """
            qs = super(MigrateMemberAuth, self).list_from()

            # type_id = 2. Only migrate normal 'member' accounts.
            # Let's migrate 'organization', 'company' and 'school' accounts later.
            qs = qs.filter(type_id=2)

            # Don't migrate users with username 'guest' and 'weg'.
            # Users 'weg' should be deleted at some point.
            # Users 'guest' should be turned into 'guest' users.
            qs = qs.exclude(username='guest').exclude(username='weg')

            # Include profile in query, speeding it up a bit
            qs.select_related('profile')

            return qs

        def migrate_profile(instance, fieldname):
            """
            first_name = mem_profile.firstname, see 5
            last_name  = mem_profile.lastname, see 5
            """
            profile = getattr(instance, fieldname)

            if profile:
                return {
                    'first_name': crop_field(profile, 'firstname', 30) or '',
                    'last_name': crop_field(profile, 'lastname', 30) or ''
                }

            # Not every user has a profile, so don't worry
            return {}

        def migrate_single(self, from_instance, to_instance):
            super(MigrateMemberAuth, self).migrate_single(from_instance, to_instance)

            # Check whether this username already exists. If so, add a number
            counter = 1

            # Detect and change duplicate usernames
            qs = self.list_to()
            qs.exclude(pk=to_instance.pk)

            while qs.filter(username=to_instance.username).exists():
                to_instance.username = '%s-%s-%d' % (
                    from_instance.username, self.changed_marker, counter
                )

                logger.warn('Duplicate username %s for user %s, changing to %s',
                    from_instance.username, repr(from_instance), to_instance.username
                )

                counter += 1

            while qs.filter(email=to_instance.email).exists():
                to_instance.email = '%s-%s-%d' % (
                from_instance.email, self.changed_marker, counter
                )

                logger.warn('Duplicate email %s for user %s, changing to %s',
                    from_instance.email, repr(from_instance), to_instance.email
                )

                counter += 1



Migration base class
********************

.. automodule:: legacy.legacymigration.base
    :members:


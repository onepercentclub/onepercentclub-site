Legacy migration
================

Migration base class
********************

.. automodule:: legacy.legacymigration.base
    :members:

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

            'password': lambda p, i: {'password': 'legacy$%s' % p},
            # A function can be specified to yield a dictionary

            'created': lambda x, i: {'date_joined': localize_datetime(x, i)},
            'updated': lambda x, i: {'last_login': localize_datetime(x, i)},
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

        def migrate_profile(profile, instance):
            """
            first_name = mem_profile.firstname, see 5
            last_name  = mem_profile.lastname, see 5
            """
            if profile:
                return {
                    'first_name': crop_field(profile.firstname, instance, 30) or '',
                    'last_name': crop_field(profile.lastname, instance, 30) or ''
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


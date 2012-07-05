import logging
logger = logging.getLogger(__name__)

from django.db import transaction


class MigrateModel(object):
    """
    Generic migration class, from one model class to another.
    """

    from_db = 'legacy'
    to_db = 'default'

    def copy_fields(self, from_instance, to_instance):
        """
        Copy all fields from one object to another.

        Example field mapping::

            field_mapping = {
                'id': None, # None means just copy the field
                'email': None,
                'username': None,
                'password': lambda instance, fieldname: {'password': getattr(instance, fieldname)}, # A function can be specified to yield a dictionary
                'created': 'date_joined', # A string can be passed to map to a different field
            }

        """

        for field, mapping in self.field_mapping.iteritems():
            if not mapping:
                # None means just copy the field
                mapping = lambda instance, field: {field: getattr(instance, field)}

            elif isinstance(mapping, basestring):
                # A string can be passed to map to a different field
                new_field = mapping
                mapping = lambda instance, field: {new_field: getattr(instance, field)}

            # By this time mapping should be a callable yielding a dict
            assert callable(mapping)

            # Mapping functions have the signature mappping(value, instance)
            value_dict = mapping(from_instance, field)

            assert isinstance(value_dict, dict), \
                'Mapping does not return a dict.'

            for (new_field, new_value) in value_dict.iteritems():
                assert isinstance(new_field, basestring)

                setattr(to_instance, new_field, new_value)

    def list_from(self):
        """
        Return an iterable with all objects to be mapped to the new model.
        """

        # Default is to return all objects
        return self.from_model.objects.using(self.from_db).all()

    def list_to(self):
        """
        Return an iterable with all the new objects that have been mapped
        from the old model.
        """

        # Default is to return all objects
        return self.to_model.objects.using(self.to_db).all()

    def get_correspondence_args(self, other_object):
        """
        Return the kwargs used for finding correspondence between one object
        and another. By default, correspondence by PK is used.
        """

        return {'pk': other_object.pk}

    def get_to(self, from_instance):
        """
        Given an existing 'old' instance, return the corresponding 'new'
        instance or None if no corresponding object exists.
        """

        # Default is to look up by id
        try:
            correspondence_args = self.get_correspondence_args(from_instance)

            return self.list_to().get(**correspondence_args)

        except self.to_model.DoesNotExist:
            return None

    def get_from(self, to_instance):
        """
        Given an existing 'new' instance, return the corresponding 'old'
        instance or None if no corresponding object exists.
        """

        # Default is to look up by id
        try:
            correspondence_args = self.get_correspondence_args(to_instance)

            return self.list_from().get(**correspondence_args)

        except self.from_model.DoesNotExist:
            return None

    def test_single(self, from_instance, to_instance):
        """
        Test the migration for a single object. Override this.

        Returns True on success, False on error.
        """

        logger.debug("Testing migration of '%s' to '%s'",
            repr(from_instance), repr(to_instance))

        return True

    def test_multiple(self, from_qs):
        """
        Test the migration for all objects in to_qs.

        By default, make sure we have at least correspondance.

        Returns True on success, False on error.
        """

        success = True

        # Test bi-directional correspondance
        for from_instance in from_qs:
            if not self.get_to(from_instance):
                logger.error('No forwards correspondence from %s',
                    repr(from_instance))

                success = False

        for to_instance in self.list_to():
            from_instance = self.get_from(to_instance)

            if not from_instance:
                logger.error('No backwards correspondence to %s.',
                    repr(to_instance))
                success = False

            if not from_instance in from_qs:
                logger.error('Correspondence %s not found in source queryset.',
                    repr(from_instance))
                success = False

            if not self.test_single(from_instance, to_instance):
                success = False

        return success

    def migrate_single(self, from_instance, to_instance):
        """ Migrate a single object. """

        logger.debug("Migrating '%s' to '%s'",
            repr(from_instance), repr(to_instance))

        self.copy_fields(from_instance, to_instance)

    def migrate_all(self):
        """ Migrate all the objects returned by list_from(). """

        # Grab a qs of object to migrate
        from_qs = self.list_from()

        counter = 0

        # Execute all of this within a single transaction
        with transaction.commit_on_success():

            # Iterate over all instances
            for from_instance in from_qs:
                to_instance = self.get_to(from_instance)

                # Not existing? Create one!
                if not to_instance:
                    to_instance = self.to_model()

                self.migrate_single(from_instance, to_instance)

                to_instance.save(using=self.to_db)
                counter += 1

                # Print a progress message very 10 objects
                if (counter % 50) == 0:
                    logger.info('%d objects migrated', counter)

            logger.info('Done migrating, performing integrity tests.')

            if not self.test_multiple(from_qs):
                raise Exception('Integrity tests failed, not committing changes.')

        logger.info('Migration %s complete.', self.__class__.__name__)
        logger.info('%d objects migrated', counter)

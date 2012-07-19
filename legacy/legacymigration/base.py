import logging
logger = logging.getLogger(__name__)

from django.db import transaction
from django.core.exceptions import (
    ValidationError, NON_FIELD_ERRORS, ObjectDoesNotExist
)

from .mappings import IdentityMapping, NullMapping, RelatedObjectMapping

from .utils import Timer


class MigrateModel(object):
    """
    Generic migration class, from one model class to another.
    """

    from_db = 'legacy'
    to_db = 'default'

    def __repr__(self):
        return self.__class__.__name__

    def get_mapping(self, field):
        """
        Get the mapping object for the specified field from `field_mapping`.
        """
        mapping = self.field_mapping.get(field)

        if mapping == True:
            # True means just copy the field
            mapping = IdentityMapping()

        elif mapping == None:
            # None means: throw away the data
            mapping = NullMapping()

        elif isinstance(mapping, basestring):
            # A string can be passed to map to a different field
            mapping = IdentityMapping(mapping)

        elif isinstance(mapping, dict):
            # Instance maps a related object to a destination object
            mapping = RelatedObjectMapping(mapping)

        # By this time mapping should be a callable yielding a dict
        assert callable(mapping), \
            u'No forward mapping defined for mapping %s' % mapping

        return mapping

    def map_fields(self, from_instance, to_instance):
        """
        Copy all fields from one object to another.
        """

        for field in self.field_mapping.iterkeys():
            # Get the mapping
            mapping = self.get_mapping(field)

            value_dict = mapping(from_instance, field)

            assert isinstance(value_dict, dict), \
                'Mapping %s returned %s instead of a dict.' % \
                    (mapping, value_dict)

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

    def get_to_correspondence(self, other_object):
        """
        Return the kwargs used for finding correspondence between one object
        and another. By default, correspondence by PK is used.
        """

        return {'pk': other_object.pk}

    def get_from_correspondence(self, other_object):
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
            correspondence_args = self.get_to_correspondence(from_instance)

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
            correspondence_args = self.get_from_correspondence(to_instance)

            return self.list_from().get(**correspondence_args)

        except self.from_model.DoesNotExist:
            return None

    def test_map_fields(self, from_instance, to_instance):
        """ Test mapping of fields. """

        success = True

        for from_field in self.field_mapping.iterkeys():
            # Get the mapping
            mapping = self.get_mapping(from_field)

            if not mapping.check(from_instance, to_instance, from_field):
                logger.error(
                    u"Mapping '%s' for field '%s' on '%s' does not correspond",
                    mapping, from_field, repr(from_instance)
                )

                success = False

        return success


    def test_single(self, from_instance, to_instance):
        """
        Test the migration for a single object. Override this.

        Returns True on success, False on error.
        """
        assert from_instance
        assert to_instance

        logger.debug(u"Testing migration of '%s' to '%s'",
            repr(from_instance), repr(to_instance))

        return self.test_map_fields(from_instance, to_instance)

    def test_multiple(self, from_qs):
        """
        Test the migration for all objects in to_qs.

        By default, make sure we have at least correspondance.

        Returns True on success, False on error.
        """

        success = True

        # Make sure we have the same number of source and destination objects
        from_count = self.list_from().count()
        to_count = self.list_to().count()
        if from_count != to_count:
            logger.error(
                u'Source queryset contains %d objects while destination queryset contains %d',
                from_count, to_count
            )

            success = False

        # Do per-object checks
        counter = 0
        errors = 0

        for to_instance in self.list_to():
            check_success = True

            from_instance = self.get_from(to_instance)

            if from_instance:
                if self.get_to(from_instance) != to_instance:
                    # TODO: This error should cause the other tests not to run AFAIK
                    logger.error(u'No bi-directional correspondence from %s to %s',
                        repr(from_instance), repr(to_instance))

                    check_success = False

                logger.debug(
                    u"Correspondence found from '%s' to '%s'.",
                    repr(from_instance), repr(to_instance)
                )

                if from_instance in from_qs:
                    if not self.test_single(from_instance, to_instance):
                        check_success = False

                else:
                    logger.error(
                        u'Correspondence %s not found in source queryset.',
                        repr(from_instance)
                    )

                    check_success = False

            else:
                logger.error(
                    u'No backwards correspondence to %s, skipping tests for this object.',
                    repr(to_instance)
                )

                check_success = False

            counter += 1

            if not check_success:
                errors += 1
                success = False

            # Print a progress message very 10 objects
            if (counter % 50) == 0:
                logger.info('%d objects tested', counter)

        logger.info('%d objects tested, %d fails', counter, errors)

        return success

    def validate_single(self, instance):
        """
        Perform model validation for an instance and report back any errors.
        """

        try:
            instance.full_clean()

        except ValidationError as e:
            for (field, errors) in e.message_dict.iteritems():
                for error in errors:
                    if field is NON_FIELD_ERRORS:
                        logger.warning(
                            u"General validation error for '%s': %s",
                            instance, error
                        )
                    else:
                        try:
                            value = getattr(instance, field)
                        except ObjectDoesNotExist:
                            value = '<Not Found>'

                        logger.warning(
                            u"Validation error for field '%s' with value '%s' of '%s': %s",
                            field, value, instance, error
                        )

            # Eventually, we should *not* let these errors pass
            # raise e


    def migrate_single(self, from_instance, to_instance):
        """ Migrate a single object. """

        logger.debug(u"Migrating '%s' to '%s'",
            repr(from_instance), repr(to_instance))

        self.map_fields(from_instance, to_instance)

    def _migrate_from(self, from_instance):
        to_instance = self.get_to(from_instance)

        # Not existing? Create one!
        if not to_instance:
            to_instance = self.to_model()

        self.migrate_single(from_instance, to_instance)

        # Validate the model
        # (before saving, to find any errors in a timely fashion)
        self.validate_single(to_instance)

        # Save to the database
        to_instance.save(using=self.to_db)

    def migrate_all(self):
        """ Migrate all the objects returned by list_from(). """

        logger.info(u"Starting '<%s>'", repr(self))

        # Grab a qs of object to migrate
        from_qs = self.list_from()

        counter = 0

        # Check whether all fields are properly mapped and issue
        # a warning if this is not the case.
        from_fields = from_qs.model._meta.get_all_field_names()

        for from_field in from_fields:
            if from_field not in self.field_mapping:
                logger.warning(
                    u"Field '%s' is not mapped and will be thrown away. To get rid of this warning, please map the field to `None` to throw away the data.",
                    from_field
                )

        # Execute all of this within a single transaction
        with transaction.commit_on_success():

            with Timer() as t:
                # Iterate over all instances
                for from_instance in from_qs:
                    self._migrate_from(from_instance)

                    counter += 1

                    # Print a progress message very 10 objects
                    if (counter % 50) == 0:
                        logger.info(u'%d objects migrated', counter)

            logger.info(u'Migration performed in %.03f seconds.', t.interval)
            logger.info(u'Starting integrity tests.')

            with Timer() as t:
                if not self.test_multiple(from_qs):
                    raise Exception('Integrity tests failed, not committing changes.')

            logger.info(
                u'Integrity tests completed in %.03f seconds.',
                t.interval
            )

        logger.info(u'%d objects migrated', counter)
        logger.info(u'Migration %s complete.', self.__class__.__name__)

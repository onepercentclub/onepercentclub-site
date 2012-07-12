import logging
logger = logging.getLogger(__name__)

from pytz.exceptions import AmbiguousTimeError

from datetime import datetime
from django.utils import timezone

from django.template.defaultfilters import slugify


class Mapping(object):
    """ Base class for mappings. """

    def __call__(self, instance, from_field):
        """ Just wrap to a more verbose map function. """

        return self.map(instance, from_field)

    def __repr__(self):
        return '<%s>' % self.__class__.__name__


class NullMapping(Mapping):
    """ Mapping that, essentially just throws away the data. """

    def map(self, instance, from_field):
        return {}

    def check(self, from_instance, to_instance, from_field):
        return True


class IdentityMapping(Mapping):
    """
    Identity mapping, allowing for mapping to a different field if `to_field`
    is specified and maps to the same fieldname of the original object
    otherwise.

    The property verbose
    """

    def __init__(self, to_field=None, verbose=True):
        self.to_field = to_field
        self.verbose = verbose

    def get_to_field(self, from_field):
        if self.to_field:
            return self.to_field

        return from_field

    def map_value(self, old_value):
        """
        Convenient wrapping function for filtering values.
        """

        return old_value

    def map(self, instance, from_field):
        old_value = getattr(instance, from_field)
        new_value = self.map_value(old_value)

        if old_value is not new_value:
            if self.verbose:
                logger.warning(
                    "Field '%s' on '%s' mapped from '%s' to '%s' by '%s'.",
                    from_field, repr(instance),
                    old_value, new_value, repr(self)
                )

        return {self.get_to_field(from_field): new_value}

    def check_value(self, old_value, new_value):
        return self.map_value(old_value) == new_value

    def check(self, from_instance, to_instance, from_field):
        old_value = getattr(from_instance, from_field)
        new_value = getattr(to_instance, self.get_to_field(from_field))

        return self.check_value(old_value, new_value)


class NoneToStringMapping(IdentityMapping):
    """
    Identity mapping but for strings returns '' where None comes in.
    """

    def map_value(self, old_value):
        old_value = super(NoneToStringMapping, self).map_value(old_value)

        if old_value == None:
            return ''

        return old_value


class CropMapping(IdentityMapping):
    """
    Subclass of the IdentityMapping, doing automated cropping of field data
    during the mapping.
    """
    def __init__(self, length, *args, **kwargs):
        self.length = length

        super(CropMapping, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<%s: %d characters>' % (self.__class__.__name__, self.length)

    def map_value(self, old_value):
        old_value = super(CropMapping, self).map_value(old_value)

        return old_value[:self.length]


class EducateDateTimeMapping(IdentityMapping):
    """
    Mapping that educates datetime objects.
    """
    def __init__(self, tz=None, **kwargs):
        """ Specify the timezone for the mapping. """

        # Default to default timezone if none is given
        if not tz:
            tz = timezone.get_default_timezone()

        self.tz = tz

        super(EducateDateTimeMapping, self).__init__(**kwargs)

    def map_value(self, old_value):
        old_value = super(EducateDateTimeMapping, self).map_value(old_value)

        # Ain't no localized None
        if old_value is None:
                return old_value

        assert isinstance(old_value, datetime)

        if timezone.is_naive(old_value):
            try:
                return self.tz.localize(old_value)
            except AmbiguousTimeError:
                logger.warning(
                    "Ambiguous datetime '%s' encountered, assuming DST.",
                    old_value
                )

                return self.tz.localize(old_value, is_dst=True)

        return old_value


class SubstitutionMapping(IdentityMapping):
    """
    Mapping allowing for mapping using a generic substitution string.
    """
    def __init__(self, substitution, *args, **kwargs):
        """ Specify the substitution string, ie. 'banana%sbanana'. """

        self.substitution = substitution

        super(SubstitutionMapping, self).__init__(*args, **kwargs)

    def map_value(self, old_value):
        return self.substitution % old_value


class SlugifyMapping(IdentityMapping):
    """
    Mapping to create a slug out of the original value.
    """

    def map_value(self, old_value):
        return slugify(old_value)


class SlugifyCroppingMapping(CropMapping, SlugifyMapping):
    pass


class OneToManyMapping(Mapping):
    """
    Mapping from one field to many, each using their particular mapping.

    Use as such::

        OneToManyMapping(
            MyMapping(to_field='Banaan'),
            ...
        )
    """
    def __init__(self, *args):
        """ Interpret all positional arguments as Mapping objects. """
        self.mappings = args

    def map(self, instance, from_field):
        result_dict = {}

        for mapping in self.mappings:
            value_dict = mapping(instance, from_field)

            assert isinstance(value_dict, dict), \
                'Mapping %s returned %s instead of a dict.' % \
                    (mapping, value_dict)

            result_dict.update(value_dict)

        return result_dict

    def check(self, from_instance, to_instance, from_field):
        success = True

        for mapping in self.mappings:
            check_result = mapping.check(
                from_instance, to_instance, from_field
            )

            if not check_result:
                success = False

        return success


class RelatedObjectMapping(Mapping):
    """
    Tool to use 'mappings inside a mapping' to map related objects onto the
    destination object.
    """

    def __init__(self, field_mapping, verbose=True):
        self.field_mapping = field_mapping
        self.verbose = verbose

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
            'No forward mapping defined for mapping %s' % mapping
        return mapping

    def map(self, instance, from_field):
        from_related_instance = getattr(instance, from_field)

        result_dict = {}

        # If the related property is not set, skip going into it
        if from_related_instance is not None:
            for field in self.field_mapping.iterkeys():
                # Get the mapping
                mapping = self.get_mapping(field)

                value_dict = mapping(from_related_instance, field)

                assert isinstance(value_dict, dict), \
                    'Mapping %s returned %s instead of a dict.' % \
                        (mapping, value_dict)

                result_dict.update(value_dict)

        return result_dict

    def check(self, from_instance, to_instance, from_field):
        from_related_instance = getattr(from_instance, from_field)

        success = True

        if from_related_instance:
            for from_field in self.field_mapping.iterkeys():
                # Get the mapping
                mapping = self.get_mapping(from_field)

                check_result = mapping.check(
                    from_related_instance, to_instance, from_field
                )

                if not check_result:
                    success = False

        return success


class NoneToStringCroppingMapping(CropMapping, NoneToStringMapping):
    pass


class MappingMapping(IdentityMapping):
    """
    Maps a given dictionary of old values as keys to new values.
    """

    def __init__(self, mapping, **kwargs):
        """
        Specify the `mapping` and, optionally, a `default`.
        """

        self.mapping = mapping

        self.default_set = False
        if 'default' in kwargs:
            self.default = kwargs.pop('default')
            self.default_set = True

        super(MappingMapping, self).__init__(**kwargs)

    def map_value(self, old_value):
        if old_value in self.mapping:
            return self.mapping[old_value]

        if self.default_set:
            return self.default

        raise Exception("No mapping found for value '%s'." % old_value)


class CountryMapping(IdentityMapping):
    """
    Map a Country instance to it's two-letter representation, or an empty
    string if no country value had been set before.

    When an error occurs in the lookup, assume a f*ckup and set to NULL.
    """

    def map(self, instance, from_field):
        country_id = getattr(instance, from_field+'_id')

        if country_id == 0:
            new_value = None

            logger.warning(
                "No country found for field '%s' on '%s', mapped to None.",
                    from_field, repr(instance)
            )

        else:
            old_value = getattr(instance, from_field)

            if old_value:
                new_value = old_value.code2

            if old_value is not new_value:
                if self.verbose:
                    logger.warning(
                        "Field '%s' on '%s' mapped from '%s' to '%s' by '%s'.",
                        from_field, repr(instance),
                        old_value, new_value, repr(self)
                    )

        return {self.get_to_field(from_field): new_value}

    def check(self, from_instance, to_instance, from_field):
        new_value = getattr(to_instance, self.get_to_field(from_field))
        country_id = getattr(from_instance, from_field+'_id')

        if country_id == 0:
            return new_value == None
        else:
            old_value = getattr(from_instance, from_field)

            return new_value == old_value.code2

        return self.check_value(old_value, new_value)


class NoneToStringCountryMapping(CountryMapping):
    """
    Map a Country instance to it's two-letter representation, or an empty
    string if no country value had been set before.
    """
    def map_value(self, old_value):
        if old_value is None:
            return ''

        return super(NoneToStringCountryMapping, self).map_value(old_value)


class WebsiteMapping(NoneToStringMapping):
    """
    Mapping for cleanup up website addresses.
    """
    def map_value(self, old_value):
        old_value = super(WebsiteMapping, self).map_value(old_value)

        old_value = old_value.strip()

        if old_value and old_value.startswith('//'):
            old_value = 'http:' + old_value

        if old_value and old_value.startswith('/'):
            old_value = 'http:/' + old_value

        return old_value

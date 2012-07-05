import logging
logger = logging.getLogger(__name__)

from pytz.exceptions import AmbiguousTimeError

from datetime import datetime
from django.utils import timezone

# For now, assume all datetimes are in the default timezone (not in GMT)
default_tz = timezone.get_default_timezone()


def localize_datetime(instance, fieldname):
    """ Assume all datetimes are in local time and convert them. """

    value = getattr(instance, fieldname)

    assert isinstance(value, datetime)

    if timezone.is_naive(value):
        try:
            return default_tz.localize(value)
        except AmbiguousTimeError:
            logger.warning("Ambiguous time '%s' accounted field '%s' on '%s', assuming DST.",
                value, fieldname, repr(instance)
            )

            return default_tz.localize(value, is_dst=True)

    # 'Educated' datetime, do nothing
    return value


def crop_field(instance, fieldname, length):
    """ Generic cropping code for strings, logging. """

    value = getattr(instance, fieldname)

    if value and len(value) > length:
        logger.warning("Value '%s' for field '%s' on '%s' too long, cropping to %d characters.",
            value, fieldname, repr(instance), length)

        return value[:length]

    return value

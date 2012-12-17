import sys
from django.conf import settings
from django.utils.timesince import timesince
from micawber.contrib.mcdjango import providers
from micawber.exceptions import ProviderException
from micawber.parsers import standalone_url_re, full_handler
from rest_framework.fields import Field
from sorl.thumbnail.shortcuts import get_thumbnail

import logging
logger = logging.getLogger(__name__)


# TODO Think about adding a feature to set thumbnail quality based on country.
#      This would be useful for countries with slow internet connections.
class SorlImageField(Field):

    def __init__(self, source, geometry_string, **options):
        super(SorlImageField, self).__init__(source)
        self.geometry_string = geometry_string
        self.options = options

    def to_native(self, value):
        if not value:
            return ""
        # The get_thumbnail() helper doesn't respect the THUMBNAIL_DEBUG setting
        # so we need to deal with exceptions like is done in the template tag.
        thumbnail = ""
        try:
            thumbnail = unicode(get_thumbnail(value, self.geometry_string, **self.options))
        except Exception:
            if getattr(settings, 'THUMBNAIL_DEBUG', None):
                raise
            logger.error('Thumbnail failed:', exc_info=sys.exc_info())
            return ""
        request = self.context.get('request')
        relative_url = settings.MEDIA_URL + thumbnail
        if request:
            return request.build_absolute_uri(relative_url)
        return relative_url


class TimeSinceField(Field):

    def to_native(self, value):
        if not value:
            return ""

        retval = timesince(value)
        # timesince can return two values (e.g. 18 hours, 4 minutes) but we only want to use the first one.
        if ', ' in retval:
            retval, ignore = timesince(value).split(', ')
        return retval


class OEmbedField(Field):

    def __init__(self, source, maxwidth=None, maxheight=None, **kwargs):
        super(OEmbedField, self).__init__(source)
        self.params = getattr(settings, 'MICAWBER_DEFAULT_SETTINGS', {})
        self.params.update(kwargs)
        if maxwidth and maxheight:
            self.params['maxwidth'] = maxwidth
            self.params['maxheight'] = maxheight
        elif maxwidth:
            self.params['maxwidth'] = maxwidth
            self.params.pop('maxheight', None)

    def to_native(self, value):
        if not value or not standalone_url_re.match(value):
            return ""
        url = value.strip()
        try:
            response = providers.request(url, **self.params)
        except ProviderException:
            return ""
        else:
            return full_handler(url, response, **self.params)
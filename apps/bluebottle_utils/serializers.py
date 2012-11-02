import logging
import sys
from django.conf import settings
from rest_framework.fields import Field
from sorl.thumbnail.shortcuts import get_thumbnail

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
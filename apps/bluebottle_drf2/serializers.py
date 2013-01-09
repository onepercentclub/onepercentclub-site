import sys
from django.conf import settings
from django.utils.timesince import timesince
from micawber.contrib.mcdjango import providers
from micawber.exceptions import ProviderException
from micawber.parsers import standalone_url_re, full_handler
from rest_framework.fields import Field
from rest_framework.serializers import SerializerOptions
from rest_framework import serializers
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


#
# Serializers for django_polymorphic models. See WallPost Serializers for an example on how to use this.
#
class PolymorphicSerializerOptions(SerializerOptions):

    def __init__(self, meta):
        super(PolymorphicSerializerOptions, self).__init__(meta)
        self.child_models = getattr(meta, 'child_models', None)


class PolymorphicSerializer(serializers.Serializer):

    _options_class = PolymorphicSerializerOptions

    def __init__(self, instance=None, data=None, files=None, context=None, partial=False, **kwargs):
        super(PolymorphicSerializer, self).__init__(instance, data, files, context, partial, **kwargs)
        self._child_models = {}
        for Model, Serializer in self.opts.child_models:
            self._child_models[Model] = Serializer()

    def field_to_native(self, obj, field_name):
        """
        Override so that we can use the child_model serializers.
        """
        obj = getattr(obj, self.source or field_name)

        return [self._child_models[item.__class__].to_native(item) for item in obj.all()]

    def convert_object(self, obj):
        """
        Override so that we can iterate through the child_model field items.
        """
        ret = self._dict_class()
        ret.fields = {}

        for field_name, field in self._child_models[obj.__class__].fields.items():
            key = self.get_field_key(field_name)
            value = field.field_to_native(obj, field_name)
            ret[key] = value
            ret.fields[key] = field
        return ret

import decimal
import logging
import sys
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.template.defaultfilters import linebreaks
from django.utils.html import strip_tags, urlize
from django.utils.timesince import timesince
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _
from micawber.contrib.mcdjango import providers
from micawber.exceptions import ProviderException
from micawber.parsers import standalone_url_re, full_handler
from rest_framework import serializers
from sorl.thumbnail.shortcuts import get_thumbnail


logger = logging.getLogger(__name__)


# TODO Think about adding a feature to set thumbnail quality based on country.
#      This would be useful for countries with slow internet connections.
class SorlImageField(serializers.ImageField):
    def __init__(self, source, geometry_string, **kwargs):
        self.crop = kwargs.pop('crop', 'center')
        self.colorspace = kwargs.pop('colorspace', 'RGB')
        self.geometry_string = geometry_string
        super(SorlImageField, self).__init__(source, **kwargs)


    def to_native(self, value):
        if not value:
            return ""

        # The get_thumbnail() helper doesn't respect the THUMBNAIL_DEBUG setting
        # so we need to deal with exceptions like is done in the template tag.
        thumbnail = ""
        try:
            thumbnail = unicode(get_thumbnail(value, self.geometry_string, crop=self.crop, colorspace=self.colorspace))
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


class TimeSinceField(serializers.Field):
    def to_native(self, value):
        if not value:
            return ""

        retval = timesince(value)

        # Special case for content that has just been posted.
        if retval == '0 minutes':
            return _("Just now")

        # timesince can return two values (e.g. 18 hours, 4 minutes) but we only want to use the first one.
        if ', ' in retval:
            retval, ignore = timesince(value).split(', ')
        return retval + ' ' + _("ago")


class ContentTextField(serializers.CharField):
    """
    A serializer for content text such as text field found in Reaction and TextWallPost. This serializer creates
    clickable links for text urls and adds <br/> and/or <p></p> in-place of new line characters.
    """

    def to_native(self, value):
        # Convert model instance text -> text for reading.
        text = super(ContentTextField, self).to_native(value)
        # This is equivalent to the django template filter: '{{ value|urlize|linebreaks }}'. Note: Text from the
        # database is escaped again here (on read) just as a double check for HTML / JS injection.
        text = linebreaks(urlize(text, None, True, True))
        # This ensure links open in a new window (BB-136).
        return re.sub(r'<a ', '<a target="_blank" ', text)

    def from_native(self, value):
        # Convert text -> model instance text for writing.
        text = super(ContentTextField, self).from_native(value)
        # HTML tags are stripped and any HTML / JS that is left is escaped.
        return strip_tags(text)


class OEmbedField(serializers.Field):
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
class PolymorphicSerializerOptions(serializers.SerializerOptions):
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

    def to_native(self, obj):
        """
        Override so that we can iterate through the child_model field items.
        """
        ret = self._dict_class()
        ret.fields = {}

        for field_name, field in self._child_models[obj.__class__].fields.items():
            field.initialize(parent=self, field_name=field_name)
            key = self.get_field_key(field_name)
            value = field.field_to_native(obj, field_name)
            ret[key] = value
            ret.fields[key] = field
        return ret

    def from_native(self, data, files):
        """
        Use from_native method from child serializer.
        Set object on that serializer before doing so.
        """
        obj = getattr(self, 'object', None)
        setattr(self._child_models[obj.__class__], 'object', obj)
        return self._child_models[obj.__class__].from_native(data, files)


class AuthorSerializer(serializers.ModelSerializer):
    picture = SorlImageField('userprofile.picture', '90x90', crop='center', colorspace="GRAY")

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'picture', 'username')


class PrimaryKeyGenericRelatedField(serializers.RelatedField):
    """ A field serializer for the object_id field in a GenericForeignKey. """

    read_only = False

    def __init__(self, to_model, *args, **kwargs):
        self.to_model = to_model
        queryset = self.to_model.objects.order_by('id').all()
        super(PrimaryKeyGenericRelatedField, self).__init__(*args, source='object_id', queryset=queryset, **kwargs)

    def label_from_instance(self, obj):
        return "{0} - {1}".format(smart_str(self.to_model.__unicode__(obj)), str(obj.id))

    def prepare_value(self, obj):
        # Called when preparing the ChoiceField widget from the to_model queryset.
        return obj.serializable_value('id')

    def to_native(self, obj):
        # Serialize using self.source (i.e. 'object_id').
        return obj.serializable_value(self.source)

    def field_to_native(self, obj, field_name):
        # Defer the serialization to the to_native() method.
        return self.to_native(obj)

    def from_native(self, value):
        try:
            to_instance = self.to_model.objects.get(pk=value)
        except self.to_model.DoesNotExist:
            raise ValidationError(self.error_messages['invalid'])
        else:
            return to_instance.id


class SlugGenericRelatedField(serializers.RelatedField):
    """ A field serializer for the object_id field in a GenericForeignKey based on the related model slug. """

    read_only = False

    def __init__(self, to_model, *args, **kwargs):
        self.to_model = to_model
        queryset = self.to_model.objects.order_by('id').all()
        super(SlugGenericRelatedField, self).__init__(*args, source='object_id', queryset=queryset, **kwargs)

    def label_from_instance(self, obj):
        return "{0} - {1}".format(smart_str(self.to_model.__unicode__(obj)), obj.slug)

    def prepare_value(self, to_instance):
        # Called when preparing the ChoiceField widget from the to_model queryset.
        return to_instance.serializable_value('slug')

    def to_native(self, obj):
        # Serialize using self.source (i.e. 'object_id').
        try:
            to_instance = self.to_model.objects.get(id=getattr(obj, self.source))
        except self.to_model.DoesNotExist:
            return None
        return to_instance.serializable_value('slug')

    def field_to_native(self, obj, field_name):
        # Defer the serialization to the to_native() method.
        return self.to_native(obj)

    def from_native(self, value):
        try:
            to_instance = self.to_model.objects.get(slug=value)
        except self.to_model.DoesNotExist:
            raise ValidationError(self.error_messages['invalid'])
        else:
            return to_instance.id


class ObjectBasedSerializerOptions(serializers.SerializerOptions):
    def __init__(self, meta):
        super(ObjectBasedSerializerOptions, self).__init__(meta)
        self.child_models = getattr(meta, 'child_models', None)


class ObjectBasedSerializer(serializers.Serializer):
    """
    Redirect to another Serializer based on the object type
    This is a copy-paste job from PolymorphicSerializer
    """

    _options_class = ObjectBasedSerializerOptions

    def __init__(self, instance=None, data=None, files=None, context=None, partial=False, **kwargs):
        super(ObjectBasedSerializer, self).__init__(instance, data, files, context, partial, **kwargs)
        self._child_models = {}
        for Model, Serializer in self.opts.child_models:
            self._child_models[Model] = Serializer()

    def field_to_native(self, obj, field_name):
        """
        Override so that we can use the child_model serializers.
        """
        obj = getattr(obj, self.source or field_name)

        return self._child_models[obj.__class__].to_native(obj)

    # TODO: This could be extracted into a base class and shared with Polymorphic serializer.
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

    def from_native(self, data, files):
        """
        Use from_native method from child serializer.
        Set object on that serializer before doing so.
        """
        obj = getattr(self, 'object', None)
        setattr(self._child_models[obj.__class__], 'object', obj)
        return self._child_models[obj.__class__].from_native(data, files)


class EuroField(serializers.WritableField):
    # Note: You need to override save and set the currency to 'EUR' in the Serializer where this is used.
    def to_native(self, value):
        return '{0}.{1}'.format(str(value)[:-2], str(value)[-2:])

    def from_native(self, value):
        return int(decimal.Decimal(value) * 100)

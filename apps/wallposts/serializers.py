from apps.bluebottle_drf2.serializers import SorlImageField, TimeSinceField, OEmbedField, PolymorphicSerializer
from apps.projects.models import Project
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django import forms
from rest_framework import serializers
from rest_framework import fields
from .models import MediaWallPost, TextWallPost


class AuthorSerializer(serializers.ModelSerializer):
    picture = SorlImageField('userprofile.picture', '90x90', crop='center', colorspace="GRAY")

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'picture', 'username')


class WallPostTypeField(fields.Field):
    """ A DRF2 Field for adding a type to WallPosts. """

    def __init__(self, type, **kwargs):
        super(WallPostTypeField, self).__init__(source='*', **kwargs)
        self.type = type

    def to_native(self, value):
        return self.type


class WallPostSerializerBase(serializers.ModelSerializer):
    """
        Base class serializer for wallposts.
        This is not used directly. Please subclass it.
    """
    id = fields.Field(source='wallpost_ptr_id')
    author = AuthorSerializer()
    timesince = TimeSinceField(source='created')

    class Meta:
        fields = ('id', 'url', 'type', 'author', 'created', 'timesince')


class MediaWallPostSerializer(WallPostSerializerBase):
    video_html = OEmbedField(source='video_url', maxwidth='560', maxheight='315')
    type = WallPostTypeField(type='media')

    class Meta:
        model = MediaWallPost
        fields = WallPostSerializerBase.Meta.fields + ('title', 'text', 'video_html', 'video_url')


class TextWallPostSerializer(WallPostSerializerBase):
    type = WallPostTypeField(type='text')

    class Meta:
        model = TextWallPost
        fields = WallPostSerializerBase.Meta.fields + ('text',)


class WallPostSerializer(PolymorphicSerializer):

    class Meta:
        child_models = (
            (TextWallPost, TextWallPostSerializer),
            (MediaWallPost, MediaWallPostSerializer),
            )


# Serializers specific to the ProjectWallPosts:

class ObjectIdField(fields.RelatedField):
    """ A field serializer for the object_id field in a GenericForeignKey. """

    default_read_only = False
    form_field_class = forms.ChoiceField

    def __init__(self, model, to_model, *args, **kwargs):
        model_type = ContentType.objects.get_for_model(to_model)
        queryset = model.objects.filter(content_type__pk=model_type.id).order_by('object_id').distinct('object_id')
        super(ObjectIdField, self).__init__(*args, source='object_id', queryset=queryset, **kwargs)

    def label_from_instance(self, obj):
        # TODO Make a better label here with project name or slug.
        return str(getattr(obj, self.source))

    def prepare_value(self, obj):
        return self.to_native(obj)

    def to_native(self, obj):
        # The actual serialization.
        return obj.serializable_value(self.source)

    def field_to_native(self, obj, field_name):
        return self.to_native(obj)


class ProjectTextWallPostSerializer(TextWallPostSerializer):
    """ TextWallPostSerializer with project specific customizations. """

    project_id = ObjectIdField(model=MediaWallPost, to_model=Project)
    url = fields.HyperlinkedIdentityField(view_name='project-mediawallpost-detail')

    class Meta(TextWallPostSerializer.Meta):
        # Add the project_id field.
        fields = TextWallPostSerializer.Meta.fields + ('project_id',)

    def save(self, save_m2m=True):
        # Save the project content type on save.
        project_type = ContentType.objects.get_for_model(Project)
        self.object.content_type_id = project_type.id
        super(ProjectTextWallPostSerializer, self).save(save_m2m)


class ProjectMediaWallPostSerializer(MediaWallPostSerializer):
    """ MediaWallPostSerializer with project specific customizations. """

    project_id = ObjectIdField(model=MediaWallPost, to_model=Project)
    url = fields.HyperlinkedIdentityField(view_name='project-mediawallpost-detail')

    class Meta(MediaWallPostSerializer.Meta):
        # Add the project_id field.
        fields = MediaWallPostSerializer.Meta.fields + ('project_id',)

    def save(self, save_m2m=True):
        # Save the project content type on save.
        project_type = ContentType.objects.get_for_model(Project)
        self.object.content_type_id = project_type.id
        super(ProjectMediaWallPostSerializer, self).save(save_m2m)


class ProjectWallPostSerializer(PolymorphicSerializer):
    """ Polymorphic WallPostSerializer with project specific customizations. """

    class Meta:
        child_models = (
            (TextWallPost, ProjectTextWallPostSerializer),
            (MediaWallPost, ProjectMediaWallPostSerializer),
            )

from apps.bluebottle_drf2.serializers import SorlImageField, TimeSinceField, OEmbedField, PolymorphicSerializer, AuthorSerializer
from apps.projects.models import Project
from apps.reactions.models import Reaction
from apps.reactions.serializers import ReactionSerializer
from apps.wallposts.models import WallPost
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from .models import MediaWallPost, TextWallPost
from rest_framework.fields import is_simple_callable
from rest_framework.serializers import ModelSerializer

class ToModelIdField(serializers.RelatedField):
    """ A field serializer for the object_id field in a GenericForeignKey. """

    default_read_only = False
    form_field_class = forms.ChoiceField

    def __init__(self, to_model, *args, **kwargs):
        self.to_model = to_model
        queryset = self.to_model.objects.order_by('id').all()
        super(ToModelIdField, self).__init__(*args, source='object_id', queryset=queryset, **kwargs)

    def label_from_instance(self, obj):
        return "{0} - {1}".format(str(obj.id), smart_str(self.to_model.__unicode__(obj)))

    def prepare_value(self, obj):
        return self.to_native(obj)

    def to_native(self, obj):
        # The actual serialization.
        return obj.serializable_value('id')

    def field_to_native(self, obj, field_name):
        return self.to_native(obj)

class WallPostTypeField(serializers.Field):
    """ A DRF2 Field for adding a type to WallPosts. """

    def __init__(self, type, **kwargs):
        super(WallPostTypeField, self).__init__(source='*', **kwargs)
        self.type = type

    def to_native(self, value):
        return self.type


class WallpostReactionSerializer(ReactionSerializer):
    wallpost_id = ToModelIdField(to_model=WallPost)

    class Meta(ReactionSerializer.Meta):
        fields = ReactionSerializer.Meta.fields + ('wallpost_id', )





class ManyRelatedSerializer(serializers.ManyRelatedField):
    """
        Nested Serializer WIP
    """

    def __init__(self, Serializer, *args, **kwargs):
        self.serializer = Serializer()
        super(ManyRelatedSerializer, self).__init__(*args, **kwargs)

    def to_native(self, obj):
        return self.serializer.to_native(obj)



class WallPostSerializerBase(serializers.ModelSerializer):
    """
        Base class serializer for wallposts.
        This is not used directly. Please subclass it.
    """
    id = serializers.Field(source='wallpost_ptr_id')
    author = AuthorSerializer()
    created = serializers.DateTimeField(read_only=True)
    timesince = TimeSinceField(source='created')
    reactions = ManyRelatedSerializer(WallpostReactionSerializer)

    class Meta:
        fields = ('id', 'url', 'type', 'author', 'created', 'timesince', 'reactions')


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

class ProjectTextWallPostSerializer(TextWallPostSerializer):
    """ TextWallPostSerializer with project specific customizations. """

    project_id = ToModelIdField(to_model=Project)
    url = serializers.HyperlinkedIdentityField(view_name='project-textwallpost-detail')

    class Meta(TextWallPostSerializer.Meta):
        # Add the project_id field.
        fields = TextWallPostSerializer.Meta.fields + ('project_id',)

    def save(self):
        # Save the project content type on save.
        project_type = ContentType.objects.get_for_model(Project)
        self.object.content_type_id = project_type.id
        super(ProjectTextWallPostSerializer, self).save()


class ProjectMediaWallPostSerializer(MediaWallPostSerializer):
    """ MediaWallPostSerializer with project specific customizations. """

    project_id = ToModelIdField(to_model=Project)
    url = serializers.HyperlinkedIdentityField(view_name='project-mediawallpost-detail')

    class Meta(MediaWallPostSerializer.Meta):
        # Add the project_id field.
        fields = MediaWallPostSerializer.Meta.fields + ('project_id',)

    def save(self):
        # Save the project content type on save.
        project_type = ContentType.objects.get_for_model(Project)
        self.object.content_type_id = project_type.id
        super(ProjectMediaWallPostSerializer, self).save()


class ProjectWallPostSerializer(PolymorphicSerializer):
    """ Polymorphic WallPostSerializer with project specific customizations. """

    class Meta:
        child_models = (
            (TextWallPost, ProjectTextWallPostSerializer),
            (MediaWallPost, ProjectMediaWallPostSerializer),
            )


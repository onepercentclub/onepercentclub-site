from apps.projects.models import Project
from bluebottle.accounts.serializers import UserPreviewSerializer
from bluebottle.bluebottle_drf2.serializers import OEmbedField, PolymorphicSerializer, SorlImageField, ContentTextField, ImageSerializer, PhotoSerializer
from apps.wallposts.models import WallPost, SystemWallPost
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.encoding import smart_text
from .models import MediaWallPost, TextWallPost, MediaWallPostPhoto, Reaction


# Serializer to serialize all wall-posts for an object into an array of ids
# Add a field like so:
# wallpost_ids = WallPostListSerializer()

class WallPostListSerializer(serializers.Field):

    def field_to_native(self, obj, field_name):
        content_type = ContentType.objects.get_for_model(obj)
        list = WallPost.objects.filter(object_id=obj.id).filter(content_type=content_type)
        list = list.values_list('id', flat=True).order_by('-created').all()
        return list


# Serializer for WallPost Reactions.

class ReactionSerializer(serializers.ModelSerializer):
    author = UserPreviewSerializer()
    text = ContentTextField()
    wallpost = serializers.PrimaryKeyRelatedField()
    url = serializers.HyperlinkedIdentityField(view_name="wallpost-reaction-detail")

    class Meta:
        model = Reaction
        fields = ('created', 'author', 'text', 'id', 'wallpost', 'url')


# Serializers for WallPosts.

class WallPostTypeField(serializers.Field):
    """ Used to add a type to WallPosts (e.g. media, text etc). """

    def __init__(self, type, **kwargs):
        super(WallPostTypeField, self).__init__(source='*', **kwargs)
        self.type = type

    def to_native(self, value):
        return self.type


class WallPostContentTypeField(serializers.SlugRelatedField):
    """
    Field to save content_type on wall-posts.
    """

    # To avoid stale apps in ContentType we white-list the apps we want to use.
    # This avoids errors like "get() returned more than one ContentType -- it returned 2!".
    white_listed_apps = ['projects', 'tasks', 'fundraisers']

    def initialize(self, parent, field_name):
        super(WallPostContentTypeField, self).initialize(parent, field_name)
        self.queryset = self.queryset.filter(app_label__in=self.white_listed_apps)


class WallPostParentIdField(serializers.IntegerField):
    """
    Field to save object_id on wall-posts.
    """

    # Make an exception for project slugs.
    def from_native(self, value):
        if not value.isnumeric():
            # Assume a project slug here
            try:
                project = Project.objects.get(slug=value)
            except Project.DoesNotExist:
                raise ValidationError("No project with that slug")
            value = project.id
        return value


class WallPostSerializerBase(serializers.ModelSerializer):
    """
        Base class serializer for WallPosts. This is not used directly; please subclass it.
    """

    author = UserPreviewSerializer()
    reactions = ReactionSerializer(many=True, read_only=True)
    parent_type = WallPostContentTypeField(slug_field='model', source='content_type')
    parent_id = WallPostParentIdField(source='object_id')

    class Meta:
        fields = ('id', 'type', 'author', 'created', 'reactions', 'parent_type', 'parent_id')


class MediaWallPostPhotoSerializer(serializers.ModelSerializer):
    photo = PhotoSerializer(required=False)
    mediawallpost = serializers.PrimaryKeyRelatedField(required=False, read_only=False)

    class Meta:
        model = MediaWallPostPhoto
        fields = ('id', 'photo', 'mediawallpost')


class MediaWallPostSerializer(WallPostSerializerBase):
    """
    Serializer for MediaWallPosts. This should not be used directly but instead should be subclassed for the specific
    model it's a WallPost about. See ProjectMediaWallPost for an example.
    """
    type = WallPostTypeField(type='media')
    text = ContentTextField(required=False)
    video_html = OEmbedField(source='video_url', maxwidth='560', maxheight='315')
    photos = MediaWallPostPhotoSerializer(many=True, required=False)
    video_url = serializers.CharField(required=False)

    class Meta:
        model = MediaWallPost
        fields = WallPostSerializerBase.Meta.fields + ('title', 'text', 'video_html', 'video_url', 'photos')


class TextWallPostSerializer(WallPostSerializerBase):
    """
    Serializer for TextWallPosts. This should not be used directly but instead should be subclassed for the specific
    model it's a WallPost about. See ProjectTextWallPost for an example.
    """
    type = WallPostTypeField(type='text')
    text = ContentTextField()

    class Meta:
        model = TextWallPost
        fields = WallPostSerializerBase.Meta.fields + ('text',)


class SystemWallPostSerializer(WallPostSerializerBase):
    """
    Serializer for TextWallPosts. This should not be used directly but instead should be subclassed for the specific
    model it's a WallPost about. See ProjectTextWallPost for an example.
    """
    type = WallPostTypeField(type='system')
    text = ContentTextField()
    related_type = serializers.CharField(source='related_type.name')

    class Meta:
        model = TextWallPost
        fields = WallPostSerializerBase.Meta.fields + ('text', 'related_type')


class WallPostSerializer(PolymorphicSerializer):

    class Meta:
        child_models = (
            (TextWallPost, TextWallPostSerializer),
            (MediaWallPost, MediaWallPostSerializer),
            (SystemWallPost, SystemWallPostSerializer),
        )

from apps.bluebottle_drf2.serializers import (OEmbedField, PolymorphicSerializer, MemberPreviewSerializer,
                                              SorlImageField, ContentTextField)
from rest_framework import serializers
from .models import MediaWallPost, TextWallPost, MediaWallPostPhoto, Reaction


# Serializer for WallPost Reactions.

class ReactionSerializer(serializers.ModelSerializer):
    author = MemberPreviewSerializer()
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


class WallPostSerializerBase(serializers.ModelSerializer):
    """
        Base class serializer for WallPosts. This is not used directly; please subclass it.
    """
    author = MemberPreviewSerializer()
    reactions = ReactionSerializer(many=True)

    class Meta:
        fields = ('id', 'type', 'author', 'created', 'reactions')


class MediaWallPostPhotoSerializer(serializers.ModelSerializer):
    photo = SorlImageField('photo', '1200x800', required=False)
    thumbnail = SorlImageField('photo', '296x296', read_only=True)
    mediawallpost = serializers.PrimaryKeyRelatedField(required=False, read_only=False)

    class Meta:
        model = MediaWallPostPhoto
        fields = ('id', 'photo', 'thumbnail', 'mediawallpost')


class MediaWallPostSerializer(WallPostSerializerBase):
    """
    Serializer for MediaWallPosts. This should not be used directly but instead should be subclassed for the specific
    model it's a WallPost about. See ProjectMediaWallPost for an example.
    """
    type = WallPostTypeField(type='media')
    text = ContentTextField(required=False)
    video_html = OEmbedField(source='video_url', maxwidth='560', maxheight='315')
    photos = MediaWallPostPhotoSerializer(many=True)

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


class WallPostSerializer(PolymorphicSerializer):

    class Meta:
        child_models = (
            (TextWallPost, TextWallPostSerializer),
            (MediaWallPost, MediaWallPostSerializer),
        )

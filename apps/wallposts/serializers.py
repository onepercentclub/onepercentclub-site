from apps.bluebottle_drf2.serializers import (TimeSinceField, OEmbedField, PolymorphicSerializer, AuthorSerializer,
                                              SorlImageField, ContentTextField)
from rest_framework import serializers
from .models import MediaWallPost, TextWallPost, MediaWallPostPhoto, Reaction


# Serializer for WallPost Reactions.

class ReactionSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    text = ContentTextField()
    timesince = TimeSinceField(source='created')
    wallpost = serializers.PrimaryKeyRelatedField()
    url = serializers.HyperlinkedIdentityField(view_name="wallpost-reaction-detail")

    class Meta:
        model = Reaction
        fields = ('created', 'author', 'text', 'id', 'timesince', 'wallpost', 'url')


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

    id = serializers.Field(source='wallpost_ptr_id')
    author = AuthorSerializer()
    timesince = TimeSinceField(source='created')
    reactions = ReactionSerializer(many=True)

    class Meta:
        fields = ('id', 'url', 'type', 'author', 'created', 'timesince', 'reactions')


class MediaWallPostPhotoSerializer(serializers.ModelSerializer):
    photo = SorlImageField('photo', '529x296')
    thumbnail = SorlImageField('photo', '296x296')

    class Meta:
        model = MediaWallPostPhoto
        fields = ('id', 'photo', 'thumbnail',)


class MediaWallPostSerializer(WallPostSerializerBase):
    """
    Serializer for MediaWallPosts. This should not be used directly but instead should be subclassed for the specific
    model it's a WallPost about. See ProjectMediaWallPost for an example.
    """

    type = WallPostTypeField(type='media')
    video_html = OEmbedField(source='video_url', maxwidth='560', maxheight='315')
    # This is temporary and will go away when we figure out how to upload related photos.
    photo = SorlImageField('photo', '529x296', required=False)
    photos = MediaWallPostPhotoSerializer(many=True)

    class Meta:
        model = MediaWallPost
        fields = WallPostSerializerBase.Meta.fields + ('title', 'text', 'video_html', 'video_url', 'photo', 'photos')


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

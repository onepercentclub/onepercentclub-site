from apps.drf2serializers.serializers import SorlImageField, TimeSinceField, OEmbedField, PolymorphicSerializer
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework import fields
from .models import MediaWallPost, TextWallPost


class AuthorSerializer(serializers.ModelSerializer):
    picture = SorlImageField('userprofile.picture', '90x90', crop='center', colorspace="GRAY")

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'picture')


class WallPostTypeField(fields.Field):
    """ A DRF2 Field for adding a type to WallPosts. """

    def __init__(self, type, **kwargs):
        super(WallPostTypeField, self).__init__(source='*', **kwargs)
        self.type = type

    def to_native(self, value):
        return self.type


class WallPostChildSerializer(serializers.ModelSerializer):
    id = fields.Field(source='wallpost_ptr_id')
    author = AuthorSerializer()
    timesince = TimeSinceField(source='created')


# Note: There is no separate list and detail serializer for MediaWallPosts
class MediaWallPostSerializer(WallPostChildSerializer):
    video_url = serializers.URLField()
    video_html = OEmbedField(source='video_url', maxwidth='560', maxheight='315')
    type = WallPostTypeField(type='media')

    class Meta:
        model = MediaWallPost
        fields = ('id', 'url', 'type', 'author', 'title', 'text', 'timesince', 'video_html')


# Note: There is no separate list and detail serializer for TextWallPosts.
class TextWallPostSerializer(WallPostChildSerializer):
    type = WallPostTypeField(type='text')

    class Meta:
        model = TextWallPost
        fields = ('id', 'url', 'type', 'author', 'text', 'timesince')


class WallPostSerializer(PolymorphicSerializer):

    class Meta:
        child_models = (
            (TextWallPost, TextWallPostSerializer),
            (MediaWallPost, MediaWallPostSerializer),
            )



# Serializers specific to the ProjectWallPosts:

class ProjectTextWallPostSerializer(TextWallPostSerializer):
    project_id = fields.PrimaryKeyRelatedField(source='object_id', read_only=True)
    url = fields.HyperlinkedIdentityField(view_name='project-wallpost-detail')

    class Meta(TextWallPostSerializer.Meta):
        fields = TextWallPostSerializer.Meta.fields + ('project_id',)


class ProjectMediaWallPostSerializer(MediaWallPostSerializer):
    project_id = fields.PrimaryKeyRelatedField(source='object_id', read_only=True)
    url = fields.HyperlinkedIdentityField(view_name='project-wallpost-detail')

    class Meta(MediaWallPostSerializer.Meta):
        fields = MediaWallPostSerializer.Meta.fields + ('project_id',)


class ProjectWallPostSerializer(PolymorphicSerializer):

    class Meta:
        child_models = (
            (TextWallPost, ProjectTextWallPostSerializer),
            (MediaWallPost, ProjectMediaWallPostSerializer),
            )

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


class WallPostChildSerializer(serializers.ModelSerializer):
    id = fields.Field(source='wallpost_ptr_id')
    author = AuthorSerializer()
    timesince = TimeSinceField(source='created')


# Note: There is no separate list and detail serializer for MediaWallPosts
class MediaWallPostSerializer(WallPostChildSerializer):
    video_url = serializers.URLField()
    video_html = OEmbedField(source='video_url', maxwidth='560', maxheight='315')

    class Meta:
        model = MediaWallPost
        fields = ('id', 'url', 'author', 'title', 'text', 'timesince', 'video_html')


# Note: There is no separate list and detail serializer for TextWallPosts.
class TextWallPostSerializer(WallPostChildSerializer):

    class Meta:
        model = TextWallPost
        fields = ('id', 'url', 'author', 'text', 'timesince')


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
        fields = TextWallPostSerializer.Meta.fields + ('project_id', 'url')


class ProjectMediaWallPostSerializer(MediaWallPostSerializer):
    project_id = fields.PrimaryKeyRelatedField(source='object_id', read_only=True)
    url = fields.HyperlinkedIdentityField(view_name='project-wallpost-detail')

    class Meta(MediaWallPostSerializer.Meta):
        fields = MediaWallPostSerializer.Meta.fields + ('project_id', 'url')


class ProjectWallPostSerializer(PolymorphicSerializer):

    class Meta:
        child_models = (
            (TextWallPost, ProjectTextWallPostSerializer),
            (MediaWallPost, ProjectMediaWallPostSerializer),
            )

from apps.drf2serializers.serializers import SorlImageField, TimeSinceField, OEmbedField
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import MediaWallPost

class AuthorSerializer(serializers.ModelSerializer):
    picture = SorlImageField('userprofile.picture', '90x90', crop='center', colorspace="GRAY")

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'picture')


# Note: There is no separate list and detail serializer for WallPosts (at least not yet).
class MediaWallPostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    timesince = TimeSinceField(source='created')
    video_url = serializers.URLField()
    video_html = OEmbedField(source='video_url', maxwidth='560', maxheight='315')

    class Meta:
        model = MediaWallPost
        fields = ('author', 'title', 'text', 'timesince', 'video_html')

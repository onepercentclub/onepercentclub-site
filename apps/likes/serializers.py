from .models import Like
from rest_framework import serializers


class LikeSerializer(serializers.ModelSerializer):

    # type = serializers.SlugRelatedField(source='content_type', slug_field='name')

    class Meta:
        model = Like
        fields = ('id', 'object_id', 'content_type', 'user')


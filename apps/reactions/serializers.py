from apps.bluebottle_drf2.serializers import AuthorSerializer
from rest_framework import serializers
from .models import Reaction


class ReactionSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    class Meta:
        model = Reaction
        fields = ('created', 'author', 'reaction', 'id')


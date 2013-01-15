from apps.bluebottle_drf2.serializers import AuthorSerializer, TimeSinceField
from rest_framework import serializers
from .models import Reaction


class ReactionSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    timesince = TimeSinceField(source='created')
    class Meta:
        model = Reaction
        fields = ('created', 'author', 'reaction', 'id', 'timesince')


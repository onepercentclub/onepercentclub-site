from apps.bluebottle_drf2.serializers import AuthorSerializer, TimeSinceField
from rest_framework import serializers
from .models import Reaction
from rest_framework.relations import HyperlinkedIdentityField


class ReactionSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    timesince = TimeSinceField(source='created')
    url = HyperlinkedIdentityField(view_name="wallpost-reaction-detail")
    class Meta:
        model = Reaction
        fields = ('created', 'author', 'reaction', 'id', 'timesince', 'url')


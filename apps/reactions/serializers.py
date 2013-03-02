from apps.bluebottle_drf2.serializers import AuthorSerializer, TimeSinceField, ContentTextField
from rest_framework import serializers
from .models import Reaction
from rest_framework.relations import HyperlinkedIdentityField


class ReactionSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    text = ContentTextField()
    timesince = TimeSinceField(source='created')
    url = HyperlinkedIdentityField(view_name="wallpost-reaction-detail")

    class Meta:
        model = Reaction
        fields = ('created', 'author', 'text', 'id', 'timesince', 'url')


from rest_framework import serializers
from .models import Reaction


class ReactionSerializer(serializers.ModelSerializer):
    created = serializers.Field()
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Reaction
        fields = ('created', 'author', 'reaction', 'id')


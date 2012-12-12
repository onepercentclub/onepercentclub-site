from rest_framework import serializers
from .models import Reaction


class ReactionDetailSerializer(serializers.ModelSerializer):
    created = serializers.Field()
    author = serializers.PrimaryKeyRelatedField(read_only=True)
#    TODO: This isn't working with the pattern: api/blogs/<slug>/reactions/<pk>
#          Delete or fix this ... we don't really need it so removing it is ok but it's nice to have.
#    url = HyperlinkedIdentityField(view_name='reactions:reaction-detail')

    class Meta:
        model = Reaction
        fields = ('created', 'author', 'reaction', 'id')


class ReactionListSerializer(ReactionDetailSerializer):

    class Meta:
        model = Reaction
        fields = ('created', 'author', 'reaction', 'id')

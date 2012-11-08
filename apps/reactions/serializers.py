from apps.bluebottle_utils.serializers import SorlImageField, SlugHyperlinkedIdentityField
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Reaction
from rest_framework.fields import HyperlinkedIdentityField


class ReactionAuthorSerializer(serializers.ModelSerializer):
    picture = SorlImageField('userprofile.picture', '90x90', crop='center')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'picture')


class ReactionDetailSerializer(serializers.ModelSerializer):
    # Read-only fields.
    created = serializers.Field()

    # Custom fields.
    author = ReactionAuthorSerializer()
#    TODO: This isn't work with the pattern: api/blogs/<slug>/reactions/<pk>
#          Delete or fix this ... we don't really need it so removing it is ok but it's nice to have.
#    url = HyperlinkedIdentityField(view_name='reactions:reaction-detail')

    class Meta:
        model = Reaction
        fields = ('created', 'author', 'reaction')


class ReactionListSerializer(ReactionDetailSerializer):

    class Meta:
        model = Reaction
        fields = ('created', 'author', 'reaction')

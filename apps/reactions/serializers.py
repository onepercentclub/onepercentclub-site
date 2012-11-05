from apps.bluebottle_utils.serializers import SorlImageField, SlugHyperlinkedIdentityField
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Reaction
from rest_framework.fields import HyperlinkedIdentityField


class ReactionOwnerSerializer(serializers.ModelSerializer):
    picture = SorlImageField('userprofile.picture', '90x90', crop='center')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'picture')


class ReactionDetailSerializer(serializers.ModelSerializer):
    # Read-only fields.
    object_pk = serializers.Field()
    created = serializers.Field()
    updated = serializers.Field()
    deleted = serializers.Field()
    ip_address = serializers.Field()

    # Custom fields.
    owner = ReactionOwnerSerializer()
    url = HyperlinkedIdentityField(view_name='reaction-detail')

    class Meta:
        model = Reaction
        exclude = ('editor',)


class ReactionListSerializer(ReactionDetailSerializer):

    class Meta:
        model = Reaction
        exclude = ('editor',)

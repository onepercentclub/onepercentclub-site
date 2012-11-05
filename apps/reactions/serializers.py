from apps.bluebottle_utils.serializers import SorlImageField, SlugHyperlinkedIdentityField
from django.contrib.auth.models import User
from fluent_contents.rendering import render_placeholder
from rest_framework import serializers
from .models import Reaction
from rest_framework.fields import HyperlinkedIdentityField


class ReactionAuthorSerializer(serializers.ModelSerializer):
    picture = SorlImageField('userprofile.picture', '90x90', crop='center')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'picture')


class ReactionDetailSerializer(serializers.ModelSerializer):
    author = ReactionAuthorSerializer()
    url = SlugHyperlinkedIdentityField(view_name='reaction-instance')

    class Meta:
        model = Reaction


class ReactionListSerializer(ReactionDetailSerializer):

    class Meta:
        model = Reaction

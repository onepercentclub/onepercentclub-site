from bluebottle.accounts.serializers import UserPreviewSerializer
from fluent_contents.rendering import render_placeholder
from rest_framework import serializers
from .models import Quote


class QuoteSerializer(serializers.ModelSerializer):
    user = UserPreviewSerializer()


    class Meta:
        model = Quote
        fields = ('id', 'quote', 'segment', 'user')

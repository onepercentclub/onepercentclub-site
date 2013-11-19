from rest_framework import serializers

from bluebottle.accounts.serializers import UserPreviewSerializer
# from bluebottle.bluebottle_utils.serializers import MetaField # TODO: later...
from bluebottle.bluebottle_drf2.serializers import EuroField, OEmbedField

from apps.fund.models import Donation
from .models import FundRaiser


class FundRaiserSerializer(serializers.ModelSerializer):
    """ Serializer to view/create fundraisers """

    owner = UserPreviewSerializer()
    project = serializers.SlugRelatedField(source='project', slug_field='slug', read_only=True)
    amount = EuroField()
    video_html = OEmbedField(source='video_url', maxwidth='560', maxheight='315')

    class Meta:
        model = FundRaiser
        fields = ('owner', 'project', 'title', 'description', 'image',
                  'video_html', 'video_url', 'amount', 'deadline')


class FundRaiserPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundRaiser
        fields = ('title', 'id')


class DonationFundRaiserSerializer(serializers.ModelSerializer):
    fundraiser = FundRaiserPreviewSerializer(read_only=True)

    class Meta:
        model = Donation
        fields = ('fundraiser',)

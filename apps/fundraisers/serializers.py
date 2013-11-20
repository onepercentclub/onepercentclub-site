from rest_framework import serializers

from bluebottle.accounts.serializers import UserPreviewSerializer
from bluebottle.bluebottle_drf2.serializers import EuroField, ImageSerializer, OEmbedField

from bluebottle.bluebottle_utils.serializers import MetaField

from apps.fund.models import Donation
from .models import FundRaiser


class FundRaiserSerializer(serializers.ModelSerializer):
    """ Serializer to view/create fundraisers """

    owner = UserPreviewSerializer(read_only=True)
    project = serializers.SlugRelatedField(source='project', slug_field='slug')
    image = ImageSerializer()
    amount = EuroField()
    amount_donated = EuroField(source='amount_donated', read_only=True)
    video_html = OEmbedField(source='video_url', maxwidth='560', maxheight='315')

    meta_data = MetaField(
            title = 'get_meta_title', # TODO: specific title format
            image_source = 'image',
            tweet = 'get_tweet',
            )

    class Meta:
        model = FundRaiser
        fields = ('id', 'owner', 'project', 'title', 'description', 'image',
                  'video_html', 'video_url', 'amount', 'deadline',
                  'amount_donated', 'meta_data')


class FundRaiserPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundRaiser
        fields = ('title', 'id')


class DonationFundRaiserSerializer(serializers.ModelSerializer):
    fundraiser = FundRaiserPreviewSerializer(read_only=True)

    class Meta:
        model = Donation
        fields = ('fundraiser',)

from rest_framework import serializers

from bluebottle.bluebottle_drf2.serializers import EuroField

from .models import Campaign


class CampaignSerializer(serializers.ModelSerializer):
    target = EuroField()
    amount_donated = EuroField(source='sum_donations', read_only=True)

    class Meta:
        model = Campaign
        fields = ('id', 'title', 'start', 'end', 'target', 'amount_donated')
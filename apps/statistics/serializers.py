from bluebottle.bb_accounts.serializers import UserPreviewSerializer
from rest_framework import serializers
from bluebottle.bluebottle_drf2.serializers import EuroField
from .models import Statistic


class StatisticSerializer(serializers.ModelSerializer):

    donated = EuroField(source='donated')

    class Meta:
        model = Statistic
        fields = ('donated', 'lives_changed', 'projects', 'countries', 'hours_spent')

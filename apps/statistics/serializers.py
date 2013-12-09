from bluebottle.accounts.serializers import UserPreviewSerializer
from rest_framework import serializers
from .models import Statistic


class StatisticSerializer(serializers.ModelSerializer):

    donated = serializers.IntegerField(source='donated')

    class Meta:
        model = Statistic
        fields = ('donated', 'lives_changed', 'projects', 'countries', 'hours_spent')

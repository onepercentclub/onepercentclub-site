from bluebottle.accounts.serializers import UserPreviewSerializer
from rest_framework import serializers
from .models import Statistic


class StatisticSerializer(serializers.ModelSerializer):

    class Meta:
        model = Statistic

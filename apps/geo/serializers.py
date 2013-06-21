from apps.geo.models import Country
from rest_framework import serializers


class CountrySerializer(serializers.ModelSerializer):
    code = serializers.CharField(source='alpha2_code')

    class Meta:
        model = Country
        fields = ('id', 'name', 'code')

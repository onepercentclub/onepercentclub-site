from apps.geo.models import Country
from rest_framework import serializers


class CountrySerializer(serializers.ModelSerializer):
    code = serializers.CharField(source='alpha2_code')
    oda = serializers.BooleanField(source='oda_recipient')
    oda = serializers.BooleanField(source='oda_recipient')

    class Meta:
        model = Country
        fields = ('id', 'name', 'code', 'oda')

from apps.geo.models import Country
from rest_framework import serializers

class CountrySerializer(serializers.ModelSerializer):
    value = serializers.Field(source='alpha2_code')
    title = serializers.Field(source='name')

    class Meta:
        model = Country
        fields = ('value', 'title')
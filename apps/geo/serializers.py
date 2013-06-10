from apps.geo.models import Country
from rest_framework import serializers


class CountrySerializer(serializers.ModelSerializer):

     class Meta:
        model = Country
        fields = ('id', 'name')
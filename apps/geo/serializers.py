from apps.geo.models import Country
from apps.projects.models import ProjectTheme
from rest_framework import serializers


class CountrySerializer(serializers.ModelSerializer):
    # Can't use 'id' because it doesn't work with 'optionValuePath' in Em.Select.
    pk = serializers.Field(source='id')
    code = serializers.Field(source='alpha2_code')
    title = serializers.Field(source='name')

    class Meta:
        model = Country
        fields = ('pk', 'code', 'title')

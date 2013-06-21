from apps.bluebottle_utils.models import Address
from apps.projects.models import ProjectTheme
from rest_framework import serializers


class ThemeSerializer(serializers.ModelSerializer):
    title = serializers.Field(source='name')

    class Meta:
        model = ProjectTheme
        fields = ('id', 'title')


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = ('id', 'line1', 'line2', 'city', 'state', 'country', 'postal_code')


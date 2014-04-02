from django.contrib.auth import get_user_model
from rest_framework import serializers
from bluebottle.bb_accounts.serializers import (UserProfileSerializer as BaseUserProfileSerializer,
                                                UserSettingsSerializer as BaseUserSettingsSerializer)
from bluebottle.geo.models import Country
from .models import UserAddress

USER_MODEL = get_user_model()


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('name',)

class UserAddressSerializer(serializers.ModelSerializer):
    country = CountrySerializer(source="country")

    class Meta:
        model = UserAddress
        fields = ('line1','line2', 'address_type', 'city', 'state', 'country', 'postal_code')

class UserProfileSerializer(BaseUserProfileSerializer):

    class Meta:
        model = BaseUserProfileSerializer.Meta.model
        fields = BaseUserProfileSerializer.Meta.fields


class UserSettingsSerializer(BaseUserSettingsSerializer):
    address = UserAddressSerializer(source='address')

    class Meta:
        model = BaseUserSettingsSerializer.Meta.model
        fields = BaseUserSettingsSerializer.Meta.fields + ('address',)

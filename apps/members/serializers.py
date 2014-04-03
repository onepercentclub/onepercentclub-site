from django.contrib.auth import get_user_model
from rest_framework import serializers
from bluebottle.bb_accounts.serializers import (UserProfileSerializer as BaseUserProfileSerializer,
                                                UserSettingsSerializer as BaseUserSettingsSerializer)
from .models import UserAddress
from bluebottle.geo.serializers import CountrySerializer

USER_MODEL = get_user_model()


class UserAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAddress
        fields = ('id', 'line1','line2', 'address_type', 'city', 'state', 'country', 'postal_code')

class UserProfileSerializer(BaseUserProfileSerializer):

    class Meta:
        model = BaseUserProfileSerializer.Meta.model
        fields = BaseUserProfileSerializer.Meta.fields


class UserSettingsSerializer(BaseUserSettingsSerializer):
    address = UserAddressSerializer(source='address')

    class Meta:
        model = BaseUserSettingsSerializer.Meta.model
        fields = BaseUserSettingsSerializer.Meta.fields + ('address',)

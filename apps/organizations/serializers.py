from apps.bluebottle_drf2.serializers import TagSerializer, TaggableSerializerMixin
from rest_framework import serializers
from .models import Organization


class OrganizationSerializer(TaggableSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ('id', 'name', 'slug', 'description', 'website')


class ManageOrganizationSerializer(OrganizationSerializer):

    class Meta:
        model = Organization
        fields = ('id', 'name', 'slug', 'description', 'website',
                  'account_bank_name', 'account_bank_address', 'account_bank_country', 'account_iban', 'account_bic',
                  'account_number', 'account_name', 'account_city', 'account_other')

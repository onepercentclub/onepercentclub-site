from apps.bluebottle_drf2.serializers import TaggableSerializerMixin
from apps.bluebottle_utils.serializers import AddressSerializer
from apps.organizations.models import OrganizationAddress
from rest_framework import serializers
from .models import Organization


class OrganizationSerializer(TaggableSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ('id', 'name', 'slug', 'description', 'website')


class OrganizationAddressSerializer(AddressSerializer):

    class Meta:
        model = OrganizationAddress
        fields = AddressSerializer.Meta.fields + ('type', 'organization')


class ManageOrganizationSerializer(OrganizationSerializer):

    slug = serializers.SlugField(required=False)

#    address_ids = serializers.PrimaryKeyRelatedField(many=True, source='organizationaddress_set')
    addresses = OrganizationAddressSerializer(many=True, source='organizationaddress_set')

    class Meta:
        model = Organization
        fields = ('id', 'name', 'slug', 'description', 'website', 'email', 'twitter', 'facebook', 'skype',
                  'account_bank_name', 'account_bank_address', 'account_bank_country', 'account_iban', 'account_bic',
                  'account_number', 'account_name', 'account_city', 'account_other', 'addresses')

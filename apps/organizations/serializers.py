from django_iban.validators import iban_validator, swift_bic_validator
from rest_framework import serializers

from bluebottle.bluebottle_drf2.serializers import PrivateFileSerializer
from bluebottle.utils.serializers import AddressSerializer, URLField

from .models import Organization, OrganizationDocument

from bluebottle.bb_organizations.serializers import (OrganizationSerializer as BaseOrganizationSerializer,
                                                     ManageOrganizationSerializer as BaseManageOrganizationSerializer)


class OrganizationSerializer(BaseOrganizationSerializer):

    class Meta(BaseOrganizationSerializer):
        model = BaseOrganizationSerializer.Meta.model
        fields = BaseOrganizationSerializer.Meta.fields


class OrganizationDocumentSerializer(serializers.ModelSerializer):

    file = PrivateFileSerializer()

    class Meta:
        model = OrganizationDocument
        fields = ('id', 'organization', 'file')


class ManageOrganizationSerializer(BaseManageOrganizationSerializer):

    slug = serializers.SlugField(required=False)

    def validate_account_iban(self, attrs, source):
        value = attrs[source]
        if value:
            iban_validator(value)
        return attrs

    def validate_account_bic(self, attrs, source):
        value = attrs[source]
        if value:
            swift_bic_validator(value)
        return attrs

    class Meta(BaseManageOrganizationSerializer):
        model = BaseManageOrganizationSerializer.Meta.model
        fields = BaseManageOrganizationSerializer.Meta.fields + ( 'account_holder_name', 'account_holder_address', 'account_holder_postal_code', 
                    'account_holder_city', 'account_holder_country', 'account_iban', 'account_bic', 'account_number', 'account_bank_name',
                    'account_bank_address', 'account_bank_postal_code', 'account_bank_city', 'account_bank_country', 'account_other' )
        


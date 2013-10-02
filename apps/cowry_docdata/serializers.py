from rest_framework import serializers
from bluebottle.bluebottle_utils.validators import validate_postal_code
from .models import DocDataPaymentOrder


class DocDataOrderProfileSerializer(serializers.ModelSerializer):
    # TODO Generate country list from docdata api and use ChoiceField.
    country = serializers.CharField(required=True)

    def validate_postal_code(self, attrs, source):
        value = attrs[source]
        if value:
            country_code = ''
            if 'country' in attrs:
                country_code = attrs['country']
            elif self.object:
                country_code = self.object.country

            if country_code:
                validate_postal_code(value, country_code)
        return attrs

    class Meta:
        model = DocDataPaymentOrder
        fields = ('id', 'first_name', 'last_name', 'email', 'address', 'city', 'postal_code', 'country')

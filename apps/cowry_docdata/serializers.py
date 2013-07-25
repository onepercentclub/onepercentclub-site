from rest_framework import serializers
from .models import DocDataPaymentOrder, DocDataWebDirectDirectDebit


class DocDataOrderProfileSerializer(serializers.ModelSerializer):
    # TODO Generate country list from docdata api and use ChoiceField.
    country = serializers.CharField(required=True)

    class Meta:
        model = DocDataPaymentOrder
        fields = ('id', 'first_name', 'last_name', 'email', 'address', 'city', 'postal_code', 'country')

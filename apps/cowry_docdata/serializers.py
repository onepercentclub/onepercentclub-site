from rest_framework import serializers
from .models import DocDataPayment


class DocDataOrderProfileSerializer(serializers.ModelSerializer):
    # # TODO Generate country list from docdata api and use ChoiceField.
    # country = serializers.CharField(required=True)
    serializers.Field(source='payment_ptr_id')

    class Meta:
        model = DocDataPayment
        fields = ('id', 'first_name', 'last_name', 'email', 'street', 'house_number', 'city', 'postal_code', 'country')


class DocDataPaymentMethodSerializer(serializers.Serializer):
    class Meta:
        model = DocDataPayment
        fields = ('id', 'name', 'payment_submethod', 'payment_submethods')

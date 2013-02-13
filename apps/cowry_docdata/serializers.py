from rest_framework import serializers
from .models import DocDataPayment


class DocDataOrderProfileSerializer(serializers.ModelSerializer):
    # # TODO Generate country list from docdata api and use ChoiceField.
    id = serializers.Field(source='payment_ptr_id')
    country = serializers.CharField(required=True)

    class Meta:
        model = DocDataPayment
        fields = ('id', 'first_name', 'last_name', 'email', 'street', 'city', 'postal_code', 'country')


class DocDataPaymentMethodSerializer(serializers.Serializer):
    class Meta:
        model = DocDataPayment
        fields = ('id', 'name', 'payment_submethod', 'payment_submethods')

from rest_framework import serializers
from .models import DocDataPayment


class DocDataOrderProfileSerializer(serializers.ModelSerializer):
    # email = serializers.EmailField(max_length=254, default='', blank=True)
    # first_name = serializers.CharField(max_length=255, default='', blank=True)
    # last_name = serializers.CharField(required=True)
    # street = serializers.CharField(required=True)
    # house_number = serializers.CharField(required=True)
    # postal_code = serializers.CharField(required=True)
    # city = serializers.CharField(required=True)
    # # TODO Generate country list from docdata api and use ChoiceField.
    # country = serializers.CharField(required=True)
    serializers.Field(source='payment_ptr_id')

    class Meta:
        model = DocDataPayment
        fields = ('id', 'first_name', 'last_name', 'email', 'street', 'house_number', 'city', 'postal_code', 'country')


class DocDataPaymentMethodSerializer(serializers.Serializer):
    class Meta:
        model = DocDataPayment
        fields = ('id', 'name', 'payment_submethods',)


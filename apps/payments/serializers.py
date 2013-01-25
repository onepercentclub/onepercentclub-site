from apps.bluebottle_drf2.serializers import SorlImageField
from rest_framework import serializers
from rest_framework import fields
from cowry.models import Payment, PaymentAdapter, PaymentMethod


class PaymentAdapterSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentAdapter
        fields = ('id', 'title', 'slug', 'active')


class PaymentMethodSerializer(serializers.ModelSerializer):
    payment_adapter = PaymentAdapterSerializer()
    icon = SorlImageField('icon', '90x90')

    class Meta:
        model = PaymentMethod
        fields = ('id', 'title', 'slug', 'active', 'icon', 'payment_adapter')


class PaymentSerializer(serializers.ModelSerializer):
    status = fields.Field(source='status')
    amount = fields.Field(source='amount')

    class Meta:
        model = Payment
        fields = ('id', 'created', 'status', 'amount', 'payment_method')

from apps.bluebottle_drf2.serializers import SorlImageField
from rest_framework import serializers
from rest_framework import relations
from rest_framework import fields
from .models import Donation, OrderItem
from cowry.models import Payment, PaymentAdapter, PaymentMethod


class DonationSerializer(serializers.ModelSerializer):
    project = relations.PrimaryKeyRelatedField(source='project')
    status = fields.Field()

    class Meta:
        model = Donation
        fields = ('id', 'project', 'amount', 'status')


class OrderItemSerializer(serializers.ModelSerializer):
    amount = fields.Field(source='amount')
    type = fields.Field(source='type')

    # TODO: At conditional serializers for Donation or Voucher here on source='item'

    class Meta:
        model = OrderItem
        fields = ('amount', 'type')

# Payment Serializers

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

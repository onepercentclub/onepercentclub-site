from apps.bluebottle_drf2.serializers import SorlImageField, PolymorphicSerializer
from cowry_docdata.models import DocdataPaymentInfo
from cowry_ipay.models import Payment
from rest_framework import serializers
from rest_framework import relations
from rest_framework import fields
from .models import Donation, OrderItem
from cowry.models import Payment, PaymentAdapter, PaymentMethod, PaymentInfo


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
    amount = fields.Field(source='amount')
    created = fields.Field(source='created')
    status = fields.Field(source='status')
    payment_method = relations.PrimaryKeyRelatedField(source='payment_method')

    class Meta:
        model = Payment
        fields = ('id', 'created', 'status', 'amount', 'payment_method')


class PaymentInfoSerializerBase(serializers.ModelSerializer):
    id = serializers.Field(source='paymentinfo_ptr_id')
    amount = fields.Field(source='amount')
    status = fields.Field(source='status')
    payment_url = fields.Field(source='payment_url')

    class Meta:
        model = PaymentInfo
        fields = ('id', 'created', 'status', 'amount', 'payment_url')


class DocdataPaymentInfoSerializer(PaymentInfoSerializerBase):
    email = fields.WritableField(source='client_email')
    first_name = fields.WritableField(source='client_firstname')
    last_name = fields.WritableField(source='client_lastname')
    address = fields.WritableField(source='client_address')
    city = fields.WritableField(source='client_city')
    zip_code = fields.WritableField(source='client_zip')
    country = fields.WritableField(source='client_country')

    class Meta:
        model = DocdataPaymentInfo
        fields = PaymentInfoSerializerBase.Meta.fields + ('email', 'first_name', 'last_name', 'address', 'city',
                                                      'zip_code', 'country')


class PaymentInfoSerializer(PolymorphicSerializer):

    class Meta:
        child_models = (
            (DocdataPaymentInfo, DocdataPaymentInfoSerializer),
            )

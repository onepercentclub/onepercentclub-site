# coding=utf-8
from apps.bluebottle_drf2.serializers import SorlImageField, PolymorphicSerializer, ObjectBasedSerializer
from apps.fund.models import Order
from django.utils.translation import ugettext as _
from rest_framework import serializers
from apps.cowry_docdata.models import DocdataPaymentInfo
from apps.cowry.models import Payment, PaymentAdapter, PaymentMethod, PaymentInfo
from .models import Donation, OrderItem


class DonationSerializer(serializers.ModelSerializer):
    # The duplication of project is temporary. See note in orders.js App.OrderItem.
    project_id = serializers.SlugRelatedField(source='project', slug_field='slug', read_only=True)
    project_slug = serializers.SlugRelatedField(source='project', slug_field='slug')
    status = serializers.Field()
    url = serializers.HyperlinkedIdentityField(view_name='fund-order-current-donation-detail')

    def validate_amount(self, attrs, source):
        """
        Check the amount
        """
        value = attrs[source]
        if value < 5:
            raise serializers.ValidationError(_(u"Amount must be at least €5.00."))
        return attrs


    class Meta:
        model = Donation
        fields = ('id', 'project_id', 'project_slug', 'amount', 'status', 'url')


class OrderItemObjectSerializer(ObjectBasedSerializer):

    class Meta:
        child_models = (
            (Donation, DonationSerializer),
            )


class OrderSerializer(serializers.ModelSerializer):
    amount = serializers.Field(source='amount')
    status = serializers.Field(source='status')
    recurring = serializers.BooleanField(source='recurring')

    class Meta:
        model = Order
        fields = ('id', 'amount', 'status', 'recurring')


class OrderItemSerializer(serializers.ModelSerializer):
    amount = serializers.Field(source='amount')
    type = serializers.Field(source='type')
    item = OrderItemObjectSerializer(source='content_object')

    class Meta:
        model = OrderItem
        fields = ('amount', 'type', 'item')


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
    amount = serializers.Field(source='amount')
    created = serializers.Field(source='created')
    status = serializers.Field(source='status')
    payment_method = serializers.PrimaryKeyRelatedField(source='payment_method')

    class Meta:
        model = Payment
        fields = ('id', 'created', 'status', 'amount', 'payment_method')


class PaymentInfoSerializerBase(serializers.ModelSerializer):
    id = serializers.Field(source='paymentinfo_ptr_id')
    amount = serializers.Field(source='amount')
    status = serializers.Field(source='status')
    payment_url = serializers.Field(source='payment_url')

    class Meta:
        model = PaymentInfo
        fields = ('id', 'created', 'status', 'amount', 'payment_url')


class DocdataPaymentInfoSerializer(PaymentInfoSerializerBase):
    email = serializers.WritableField(source='client_email')
    first_name = serializers.WritableField(source='client_firstname')
    last_name = serializers.WritableField(source='client_lastname')
    address = serializers.WritableField(source='client_address')
    city = serializers.WritableField(source='client_city')
    zip_code = serializers.WritableField(source='client_zip')
    country = serializers.WritableField(source='client_country')

    class Meta:
        model = DocdataPaymentInfo
        fields = PaymentInfoSerializerBase.Meta.fields + ('email', 'first_name', 'last_name', 'address', 'city',
                                                      'zip_code', 'country')


class PaymentInfoSerializer(PolymorphicSerializer):

    class Meta:
        child_models = (
            (DocdataPaymentInfo, DocdataPaymentInfoSerializer),
            )

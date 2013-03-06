# coding=utf-8
from apps.bluebottle_drf2.serializers import ObjectBasedSerializer, EuroField
from apps.fund.models import OrderItem
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _
from rest_framework import serializers
from apps.cowry import factory
from .models import Donation, Order, Voucher, CustomVoucherRequest


class DonationSerializer(serializers.ModelSerializer):
    project = serializers.SlugRelatedField(source='project', slug_field='slug')
    status = serializers.ChoiceField(read_only=True)

    # FIXME: This field makes the Donation serializer tied to '/fund/orders/current'.
    url = serializers.HyperlinkedIdentityField(view_name='fund-order-donation-detail')
    amount = EuroField()

    def validate_amount(self, attrs, source):
        """
        Check the amount
        """
        value = attrs[source]
        if value < 500:
            raise serializers.ValidationError(_(u"Amount must be at least €5.00."))
        return attrs

    def save(self):
        # Set default currency.
        self.object.currency = 'EUR'
        return super(DonationSerializer, self).save()


    class Meta:
        model = Donation
        fields = ('id', 'project', 'amount', 'status', 'url')


class VoucherSerializer(serializers.ModelSerializer):
    """
    Used for creating new Vouchers in Order screens.
    """
    amount = EuroField()
    status = serializers.Field()

    def validate_amount(self, attrs, source):
        """
        Check the amount
        """
        value = attrs[source]
        if value not in [1000, 2500, 5000, 10000]:
            raise serializers.ValidationError(_(u"Amount can only be €10, €25, €50 or €100. Not " + str(value)))
        return attrs

    def save(self):
        # Set default currency.
        self.object.currency = 'EUR'
        return super(VoucherSerializer, self).save()

    class Meta:
        model = Voucher
        fields = ('id', 'language', 'amount', 'receiver_email', 'receiver_name', 'sender_email', 'sender_name',
                  'message', 'status')


class PaymentMethodSerializer(serializers.Serializer):

    default_fields = ('id', 'name')

    def convert_object(self, obj):
        """
        Simplified converting of our object
        """
        ret = self._dict_class()
        for field_name in self.default_fields:
            ret[field_name] = obj
        return obj


class OrderSerializer(serializers.ModelSerializer):
    amount = EuroField(read_only=True)
    status = serializers.ChoiceField(read_only=True)
    # Payment_method  is writen in the view.
    payment_method_id = serializers.CharField(source='payment.payment_method_id', required=False)
    payment_submethod_id = serializers.CharField(source='payment.payment_submethod_id', required=False)

    payment_methods = serializers.SerializerMethodField(method_name='get_payment_methods')
    payment_url = serializers.SerializerMethodField(method_name='get_payment_url')

    donations = DonationSerializer(source='donations', many=True)
    vouchers = VoucherSerializer(source='vouchers', many=True)

    def get_payment_methods(self, order):
        return factory.get_payment_method_ids(amount=order.amount, currency='EUR', country='NL',
                                              recurring=order.recurring)

    def get_payment_url(self, obj):
        pm = obj.payment.latest_docdata_payment
        if pm:
            return pm.payment_url
        return None

    class Meta:
        model = Order
        fields = ('id', 'amount', 'status', 'recurring', 'payment_method_id', 'payment_methods', 'payment_submethod_id',
                  'payment_url', 'donations', 'vouchers')


class VoucherRedeemSerializer(serializers.ModelSerializer):
    """
    Used for redeeming a Voucher and setting it to 'cashed'.
    """
    amount = EuroField(read_only=True)
    language = serializers.Field()
    receiver_email = serializers.Field()
    receiver_name = serializers.Field()
    sender_email = serializers.Field()
    sender_name = serializers.Field()
    message = serializers.Field()
    donations = DonationSerializer(many=True)


    def validate_status(self, attrs, source):
        value = attrs[source]
        if value not in ['cashed']:
            raise serializers.ValidationError(_(u"Only allowed to change status to 'cashed'"))
        # TODO: Do a check if the amount of all donations for this voucher equals Voucher amount.
        # ?? self.object.amount == self.object.donations.aggregate(Sum('amount')

        return attrs


    class Meta:
        model = Voucher
        fields = ('id', 'language', 'amount', 'receiver_email', 'receiver_name', 'sender_email', 'sender_name',
                  'message', 'donations', 'status')



class VoucherDonationSerializer(DonationSerializer):
    # The duplication of project is temporary. See note in orders.js App.OrderItem.
    project_id = serializers.SlugRelatedField(source='project', slug_field='slug', read_only=True)
    project_slug = serializers.SlugRelatedField(source='project', slug_field='slug')
    status = serializers.ChoiceField(read_only=True)

    class Meta:
        model = Donation
        fields = ('id', 'project')


class OrderItemSerializer(ObjectBasedSerializer):

    def convert_object(self, obj):
        """
        Override so that we can address orderitem item.
        """
        # only show the item on the orderitem
        obj = obj.content_object

        ret = self._dict_class()
        ret.fields = {}
        for field_name, field in self._child_models[obj.__class__].fields.items():
            key = self.get_field_key(field_name)
            value = field.field_to_native(obj, field_name)
            ret[key] = value
            ret.fields[key] = field
        return ret

    class Meta:
        child_models = (
            (Donation, DonationSerializer),
            (Voucher, VoucherSerializer),
        )


class CustomVoucherRequestSerializer(serializers.ModelSerializer):
    status = serializers.Field()

    class Meta:
        model =  CustomVoucherRequest
        fields = ('id', 'status', 'amount', 'contact_name', 'contact_email', 'organization', 'message',
                  'contact_phone', 'type')

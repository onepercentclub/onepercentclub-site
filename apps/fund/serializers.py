# coding=utf-8
from apps.bluebottle_drf2.serializers import ObjectBasedSerializer, EuroField
from django.utils.translation import ugettext as _
from rest_framework import serializers
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
            raise serializers.ValidationError(_(u"Donations must be at least €5."))
        return attrs

    def save(self, **kwargs):
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
            raise serializers.ValidationError(_(u"Choose between 1%GIFTCARDS with a value of €10, €25, €50 or €100. Not " + str(value)))
        return attrs

    def save(self, **kwargs):
        # Set default currency.
        self.object.currency = 'EUR'
        return super(VoucherSerializer, self).save()

    class Meta:
        model = Voucher
        fields = ('id', 'language', 'amount', 'receiver_email', 'receiver_name', 'sender_email', 'sender_name',
                  'message', 'status')


class PaymentPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def __init__(self, *args, **kwargs):
        kwargs['read_only'] = True
        super(PaymentPrimaryKeyRelatedField, self).__init__(*args, **kwargs)

    def field_to_native(self, obj, field_name):
        payment = getattr(obj, self.source or field_name)
        if payment:
            return self.to_native(payment.id)
        return None

class OrderSerializer(serializers.ModelSerializer):
    total = EuroField(read_only=True)
    status = serializers.ChoiceField(read_only=True)
    # If we had FKs to from the donations / vouchers to the Order this could be writable.
    donations = DonationSerializer(source='donations', many=True, read_only=True)
    vouchers = VoucherSerializer(source='vouchers', many=True, read_only=True)
    payment = PaymentPrimaryKeyRelatedField(source='latest_payment')
    # This is how to show all the payments in an Order if we need it at some point.
    # payments = serializers.PrimaryKeyRelatedField(many=True)

    class Meta:
        model = Order
        fields = ('id', 'total', 'status', 'recurring', 'donations', 'vouchers', 'payment')


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
    project = serializers.SlugRelatedField(source='project', slug_field='slug')
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
        model = CustomVoucherRequest
        fields = ('id', 'status', 'number', 'contact_name', 'contact_email', 'organization', 'message',
                  'contact_phone', 'type')

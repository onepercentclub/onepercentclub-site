# coding=utf-8
from apps.bluebottle_drf2.serializers import ObjectBasedSerializer, EuroField
from apps.fund.models import close_order_after_payment
from django.utils.translation import ugettext as _
from raven.utils.serializer.base import BooleanSerializer
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


class OrderSerializer(serializers.ModelSerializer):
    total = EuroField(read_only=True)
    status = serializers.ChoiceField(read_only=True)
    donations = DonationSerializer(source='donations', many=True)
    vouchers = VoucherSerializer(source='vouchers', many=True)
    finalized = serializers.BooleanField()

    def validate_finalized(self, attrs, source):
        order = self.object
        value = attrs[source]
        if order.finalized == value:
            # No changes, carry on.
            return attrs

        if not order.finalized and value:
            # Setting order to finalized
            close_order_after_payment(order)
            return attrs

        raise serializers.ValidationError(_(u"This change of finalized state is not allowed"))

    class Meta:
        model = Order
        fields = ('id', 'total', 'status', 'recurring', 'donations', 'vouchers', 'finalized')


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
        model = CustomVoucherRequest
        fields = ('id', 'status', 'amount', 'contact_name', 'contact_email', 'organization', 'message',
                  'contact_phone', 'type')

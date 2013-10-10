# coding=utf-8
from apps.projects.serializers import ProjectPreviewSerializer
from bluebottle.accounts.serializers import UserPreviewSerializer
from bluebottle.bluebottle_drf2.serializers import EuroField
from apps.projects.models import ProjectPhases
from django.utils.translation import ugettext as _
from rest_framework import serializers
from .models import Donation, DonationStatuses, Order, OrderStatuses, Voucher, VoucherStatuses, CustomVoucherRequest, \
    RecurringDirectDebitPayment


# TODO Create a Serializer that takes an order id for the current order to make this resource RESTful.
#      The model should not have an order though.
class RecurringDirectDebitPaymentSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='recurring-direct-debit-payment-detail')
    amount = EuroField()

    class Meta:
        model = RecurringDirectDebitPayment
        fields = ('id', 'url', 'active', 'amount', 'name', 'city', 'account')


class DonationSerializer(serializers.ModelSerializer):
    project = serializers.SlugRelatedField(source='project', slug_field='slug')
    status = serializers.ChoiceField(read_only=True)
    order = serializers.PrimaryKeyRelatedField()
    amount = EuroField()
    # TODO: Enable url field.
    # This error is presented when the url field is enabled:
    #   Could not resolve URL for hyperlinked relationship using view name "fund-order-donation-detail". You may have
    #   failed to include the related model in your API, or incorrectly configured the `lookup_field` attribute on
    #   this field.
    # url = serializers.HyperlinkedIdentityField(view_name='fund-order-donation-detail')

    class Meta:
        model = Donation
        fields = ('id', 'project', 'amount', 'status', 'order')

    def validate(self, attrs):
        if self.object and self.object.status != DonationStatuses.new and attrs is not None:
                raise serializers.ValidationError(_("You cannot modify a Donation that does not have status new."))
        return attrs

    # Not using the serailizer's validation because the donation needs to be
    def validate_amount(self, attrs, source):
        #self.context.request
        value = attrs[source]

        if self.object:
            if self.object.order and self.object.order.recurring:
                if value < 200:
                    raise serializers.ValidationError(_(u"Donations must be at least €2."))
            else:
                if value < 500:
                    raise serializers.ValidationError(_(u"Donations must be at least €5."))
        else:
            if value < 500:
                raise serializers.ValidationError(_(u"Donations must be at least €5."))

        return attrs

    def validate_project(self, attrs, source):
        value = attrs[source]
        if value.phase != ProjectPhases.campaign:
            raise serializers.ValidationError(_("You can only donate a project in the campaign phase."))
        return attrs


class VoucherSerializer(serializers.ModelSerializer):
    """
    Used for creating new Vouchers in Order screens.
    """
    amount = EuroField()
    status = serializers.Field()

    def validate(self, attrs):
        if self.object and self.object.status != VoucherStatuses.new and attrs is not None:
                raise serializers.ValidationError(_("You cannot modify a Gift Card that does not have status new."))
        return attrs

    def validate_amount(self, attrs, source):
        """ Check the amount. """
        value = attrs[source]
        if value not in [1000, 2500, 5000, 10000]:
            raise serializers.ValidationError(_(u"Choose between 1%GIFTCARDS with a value of €10, €25, €50 or €100. Not " + str(value)))
        return attrs

    class Meta:
        model = Voucher
        fields = ('id', 'language', 'amount', 'receiver_email', 'receiver_name', 'sender_email', 'sender_name',
                  'message', 'status')


class OrderSerializer(serializers.ModelSerializer):
    total = EuroField(read_only=True)
    status = serializers.ChoiceField(read_only=True)
    # If we had FKs to from the donations / vouchers to the Order this could be writable.
    donations = DonationSerializer(source='donations', many=True, read_only=True)
    vouchers = VoucherSerializer(source='vouchers', many=True, read_only=True)
    payments = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='fund-order-detail')

    def validate(self, attrs):
        if self.object.status == OrderStatuses.closed and attrs is not None:
            raise serializers.ValidationError(_("You cannot modify a closed Order."))
        return attrs

    class Meta:
        model = Order
        fields = ('id', 'url', 'total', 'status', 'recurring', 'donations', 'vouchers', 'payments', 'created')


#
# Order 'current' overrides.
#

class OrderCurrentDonationSerializer(DonationSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='fund-order-current-donation-detail')
    order = serializers.SerializerMethodField('get_current_order_ember_id')

    def get_current_order_ember_id(self, donation):
        return 'current'

    class Meta:
        model = Donation
        fields = DonationSerializer.Meta.fields + ('url',)


class OrderCurrentVoucherSerializer(VoucherSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='fund-order-current-voucher-detail')


class OrderCurrentSerializer(OrderSerializer):
    # This is a hack to work around an issue with Ember-Data keeping the id as 'current'.
    id_for_ember = serializers.IntegerField(source='id', read_only=True)
    donations = OrderCurrentDonationSerializer(source='donations', many=True, read_only=True)
    vouchers = OrderCurrentVoucherSerializer(source='vouchers', many=True, read_only=True)

    class Meta:
        model = Order
        fields = OrderSerializer.Meta.fields + ('id_for_ember',)


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


class CustomVoucherRequestSerializer(serializers.ModelSerializer):
    status = serializers.Field()

    class Meta:
        model = CustomVoucherRequest
        fields = ('id', 'status', 'number', 'contact_name', 'contact_email', 'organization', 'message',
                  'contact_phone', 'type')

# For showing the latest donations
class DonationInfoSerializer(serializers.ModelSerializer):
    project = ProjectPreviewSerializer()
    user = UserPreviewSerializer()
    amount = EuroField()

    class Meta:
        model = Donation
        fields = ('id', 'project', 'amount', 'user', 'created')

# coding=utf-8
#from apps.fund.models import Donation
#from apps.fund.serializers import DonationSerializer
from bluebottle.bluebottle_drf2.serializers import EuroField
from django.utils.translation import ugettext as _
from rest_framework import serializers
from .models import Voucher, VoucherStatuses, CustomVoucherRequest


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


#
# Order 'current' overrides.
#
class OrderCurrentVoucherSerializer(VoucherSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='fund-order-current-voucher-detail')


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
    #donations = DonationSerializer(many=True)

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


#class VoucherDonationSerializer(DonationSerializer):
#    project = serializers.SlugRelatedField(source='project', slug_field='slug')
#    status = serializers.ChoiceField(read_only=True)
#
#    class Meta:
#        model = Donation
#        fields = ('id', 'project')


class CustomVoucherRequestSerializer(serializers.ModelSerializer):
    status = serializers.Field()

    class Meta:
        model = CustomVoucherRequest
        fields = ('id', 'status', 'number', 'contact_name', 'contact_email', 'organization', 'message',
                  'contact_phone', 'type')

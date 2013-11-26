# coding=utf-8
from apps.projects.serializers import ProjectPreviewSerializer
from apps.vouchers.serializers import VoucherSerializer, OrderCurrentVoucherSerializer
from bluebottle.accounts.serializers import UserPreviewSerializer
from bluebottle.bluebottle_drf2.serializers import EuroField
from apps.projects.models import ProjectPhases
from bluebottle.bluebottle_utils.serializers import MetaField
from django.utils.translation import ugettext as _
from rest_framework import serializers
from .models import Donation, DonationStatuses, Order, OrderStatuses, RecurringDirectDebitPayment


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
        fields = ('id', 'project', 'amount', 'status', 'order', 'fundraiser')

    def validate(self, attrs):
        if self.object and self.object.status != DonationStatuses.new and attrs is not None:
                raise serializers.ValidationError(_("You cannot modify a Donation that does not have status new."))
        return attrs

    def validate_amount(self, attrs, source):
        # TODO: check requirements for fundraisers
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


class RecurringDonationSerializer(serializers.ModelSerializer):

    project = serializers.SlugRelatedField(source='project', slug_field='slug')
    status = serializers.ChoiceField(read_only=True)
    order = serializers.PrimaryKeyRelatedField()
    amount = EuroField()

    class Meta:
        model = Donation
        fields = ('id', 'project', 'amount', 'status', 'order')

    def validate(self, attrs):
        if self.object and self.object.status != DonationStatuses.new and attrs is not None:
                raise serializers.ValidationError(_("You cannot modify a Donation that does not have status new."))
        return attrs

    def validate_amount(self, attrs, source):
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

    def validate_order(self, attrs, source):
        order = attrs[source]
        if not order.recurring:
            raise serializers.ValidationError(_("Can only Recurring Donations to a Recurring Order."))
        if not order.status == OrderStatuses.recurring:
            raise serializers.ValidationError(_("Can only Recurring Donations to an active Recurring Order (status recurring)."))
        return attrs



class NestedDonationSerializer(DonationSerializer):
    order = serializers.PrimaryKeyRelatedField(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    total = EuroField(read_only=True)
    status = serializers.ChoiceField(read_only=True)
    # If we had FKs to from the donations / vouchers to the Order this could be writable.
    donations = DonationSerializer(source='donations', many=True, read_only=True)
    vouchers = VoucherSerializer(source='vouchers', many=True, read_only=True)
    payments = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='fund-order-detail')

    # moste are not required because the link is pointing to a different page and facebook will look up the info on that page
    meta_data = MetaField(
            title = None,
            fb_title = None,
            description = None, # these are all not required because the link is pointing to a different page
            keywords = None,
            image_source = None,
            tweet = 'get_tweet',
            url = 'get_share_url',
            )

    def validate(self, attrs):
        if self.object.status == OrderStatuses.closed and attrs is not None:
            raise serializers.ValidationError(_("You cannot modify a closed Order."))
        return attrs

    class Meta:
        model = Order
        fields = ('id', 'url', 'total', 'status', 'recurring', 'donations', 'vouchers', 'payments', 'created', 'meta_data')


class RecurringOrderSerializer(serializers.ModelSerializer):
    total = EuroField(read_only=True)
    status = serializers.ChoiceField(read_only=True, default=OrderStatuses.recurring)
    donations = DonationSerializer(source='donations', many=True, required=False)
    recurring = serializers.BooleanField(read_only=True, default=True)

    class Meta:
        model = Order
        fields = ('id', 'total', 'status', 'donations', 'created')

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


class OrderCurrentSerializer(OrderSerializer):
    # This is a hack to work around an issue with Ember-Data keeping the id as 'current'.
    id_for_ember = serializers.IntegerField(source='id', read_only=True)
    donations = OrderCurrentDonationSerializer(source='donations', many=True, read_only=True)
    vouchers = OrderCurrentVoucherSerializer(source='vouchers', many=True, read_only=True)

    class Meta:
        model = Order
        fields = OrderSerializer.Meta.fields + ('id_for_ember',)


# For showing the latest donations
class DonationInfoSerializer(serializers.ModelSerializer):
    project = ProjectPreviewSerializer()
    user = UserPreviewSerializer()
    amount = EuroField()

    class Meta:
        model = Donation
        fields = ('id', 'project', 'amount', 'user', 'created')

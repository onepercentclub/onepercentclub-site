# coding=utf-8
from apps.bluebottle_drf2.serializers import ObjectBasedSerializer
from django.utils.translation import ugettext as _
from rest_framework import serializers
from .models import Donation, OrderItem
from .models import Order
from .utils import get_order_payment_methods


class DonationSerializer(serializers.ModelSerializer):
    # The duplication of project is temporary. See note in orders.js App.OrderItem.
    project_id = serializers.SlugRelatedField(source='project', slug_field='slug', read_only=True)
    project_slug = serializers.SlugRelatedField(source='project', slug_field='slug')
    status = serializers.ChoiceField(read_only=True)
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
    # source is required because amount is a property on the model.
    amount = serializers.IntegerField(source='amount', read_only=True)
    status = serializers.ChoiceField(read_only=True)
    # # TODO: Make a ChoiceField for payment_method to get validation on the choice.
    payment_method = serializers.CharField(source='payment.payment_method', required=False)
    payment_methods = serializers.SerializerMethodField(method_name='get_payment_methods')

    def get_payment_methods(self, obj):
        return get_order_payment_methods(obj)

    class Meta:
        model = Order
        fields = ('id', 'amount', 'status', 'recurring', 'payment_method', 'payment_methods')


class OrderItemSerializer(serializers.ModelSerializer):
    # source is required because amount and type are properties on the model.
    amount = serializers.IntegerField(source='amount', read_only=True)
    type = serializers.CharField(source='type', read_only=True)
    item = OrderItemObjectSerializer(source='content_object')

    class Meta:
        model = OrderItem
        fields = ('id', 'amount', 'type', 'item')

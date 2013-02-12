# coding=utf-8
from apps.bluebottle_drf2.serializers import ObjectBasedSerializer
from apps.fund.models import Order
from apps.cowry import factory
from django.utils.translation import ugettext as _
from rest_framework import serializers
from .models import Donation, OrderItem


class DonationSerializer(serializers.ModelSerializer):
    # The duplication of project is temporary. See note in orders.js App.OrderItem.
    project_id = serializers.SlugRelatedField(source='project', slug_field='slug', read_only=True)
    project_slug = serializers.SlugRelatedField(source='project', slug_field='slug')
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
        fields = ('id', 'project_id', 'project_slug', 'amount', 'url')


class OrderItemObjectSerializer(ObjectBasedSerializer):
    class Meta:
        child_models = (
            (Donation, DonationSerializer),
        )


class OrderSerializer(serializers.ModelSerializer):
    # source is required because amount is a property on the model.
    amount = serializers.IntegerField(source='amount', read_only=True)
    status = serializers.ChoiceField(read_only=True)
    payment_methods = serializers.SerializerMethodField(method_name='get_payment_methods')

    def get_payment_methods(self, obj):
        # Cowry payments use minor currency units so we need to convert the Euros to cents.
        amount = int(obj.amount * 100)
        return factory.get_payment_methods(amount=amount, currency='EUR', country='NL', recurring=obj.recurring)

    class Meta:
        model = Order
        fields = ('id', 'amount', 'status', 'recurring', 'payment_methods')


class OrderItemSerializer(serializers.ModelSerializer):
    # source is required because amount and type are properties on the model.
    amount = serializers.IntegerField(source='amount', read_only=True)
    type = serializers.CharField(source='type', read_only=True)
    item = OrderItemObjectSerializer(source='content_object')

    class Meta:
        model = OrderItem
        fields = ('id', 'amount', 'type', 'item')

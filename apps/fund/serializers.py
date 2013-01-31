from rest_framework import serializers
from .models import Donation, OrderItem


class DonationSerializer(serializers.ModelSerializer):
    # The duplication of project is temporary. See note in orders.js App.OrderItem.
    project = serializers.SlugRelatedField(source='project', slug_field='slug', read_only=True)
    project_slug = serializers.SlugRelatedField(source='project', slug_field='slug')
    status = serializers.Field()
    url = serializers.HyperlinkedIdentityField(view_name='fund-cart-donation-detail')

    class Meta:
        model = Donation
        fields = ('id', 'project', 'project_slug', 'amount', 'status', 'url')


class OrderItemSerializer(serializers.ModelSerializer):
    amount = serializers.Field(source='amount')
    type = serializers.Field(source='type')

    # TODO: At conditional serializers for Donation or Voucher here on source='item'

    class Meta:
        model = OrderItem
        fields = ('amount', 'type')
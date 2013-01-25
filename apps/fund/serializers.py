from apps.projects.serializers import ProjectSmallSerializer
from rest_framework import serializers
from rest_framework import relations
from rest_framework import fields
from .models import Donation, Order, OrderItem


class DonationSerializer(serializers.ModelSerializer):
    project = relations.PrimaryKeyRelatedField(source='project')
    status = fields.Field()

    class Meta:
        model = Donation
        fields = ('id', 'project', 'amount', 'status')


class OrderItemSerializer(serializers.ModelSerializer):
    amount = fields.Field(source='amount')
    type = fields.Field(source='type')

    # TODO: At conditional serializers for Donation or Voucher here on source='item'

    class Meta:
        model = OrderItem
        fields = ('amount', 'type')
from apps.bluebottle_drf2.serializers import ManyRelatedNestedSerializer
from apps.projects.serializers import ProjectSerializer
from rest_framework import serializers
from rest_framework import relations
from rest_framework import fields
from .models import Donation, Order, OrderItem


class DonationSerializer(serializers.ModelSerializer):
    project = ProjectSerializer()
    # Project_id here as a writeable field
    project_id = relations.PrimaryKeyRelatedField(source='project')
    status = fields.Field()

    class Meta:
        model = Donation
        fields = ('id', 'project', 'project_id', 'amount', 'status')


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('created', 'orderitem_set')


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ('content_type', 'object_id')
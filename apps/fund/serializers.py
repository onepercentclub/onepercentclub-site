from apps.bluebottle_drf2.serializers import ManyRelatedNestedSerializer
from apps.projects.serializers import ProjectSerializer
from rest_framework import serializers
from rest_framework import relations
from .models import Donation, Order, OrderItem


class DonationSerializer(serializers.ModelSerializer):
    project = ProjectSerializer()
    # Project_id here as a writeable field
    project_id = relations.PrimaryKeyRelatedField(source='project')

    class Meta:
        model = Donation
        fields = ('id', 'project', 'project_id', 'amount')


class OrderSerializer(serializers.ModelSerializer):
    donations = ManyRelatedNestedSerializer(DonationSerializer)
    class Meta:
        model = Order
        fields = ('created', 'donations')


class OrderItemSerializer(serializers.ModelSerializer):
    item = ManyRelatedNestedSerializer(DonationSerializer)

    class Meta:
        model = OrderItem
        fields = ('item', )
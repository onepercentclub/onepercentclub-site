from apps.bluebottle_drf2.serializers import SorlImageField
from rest_framework import serializers

from cowry.models import Payment, PaymentAdapter, PaymentMethod


class PaymentAdapterSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentAdapter
        fields = ('id', 'title', 'slug', 'active')


class PaymentMethodSerializer(serializers.ModelSerializer):
    payment_adapter = PaymentAdapterSerializer()
    icon = SorlImageField('icon', '90x90')

    class Meta:
        model = PaymentMethod
        fields = ('id', 'title', 'slug', 'active', 'icon', 'payment_adapter')


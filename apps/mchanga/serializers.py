from apps.mchanga.models import MpesaPayment, MpesaFundRaiser
from rest_framework import serializers


class MpesaPaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = MpesaPayment
        fields = ('id', 'date', 'amount', 'project', 'mpesa_name', 'mpesa_phone')


class MpesaFundRaiserSerializer(serializers.ModelSerializer):

    id = serializers.CharField(source='account')

    class Meta:
        model = MpesaFundRaiser
        fields = ('id', 'created', 'total_amount', 'current_amount')

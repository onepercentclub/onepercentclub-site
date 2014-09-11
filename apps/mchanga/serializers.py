from apps.mchanga.models import MpesaPayment
from rest_framework import serializers

class MpesaPaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = MpesaPayment
        fields = ('date', 'amount', 'project', 'mpesa_name', 'mpesa_phone')
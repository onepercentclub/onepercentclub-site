from apps.cowry_docdata.models import DocDataPaymentOrder
from django.conf import settings
from django.utils.translation import ugettext as _
from rest_framework import serializers
from . import factory, payments
from .exceptions import PaymentException
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    payment_method = serializers.CharField(source='payment_method_id', required=True)
    payment_submethod = serializers.CharField(source='payment_submethod_id', required=False)
    available_payment_methods = serializers.SerializerMethodField(method_name='get_available_payment_methods')
    payment_url = serializers.SerializerMethodField(method_name='get_payment_url')
    status = serializers.ChoiceField(read_only=True)

    def get_available_payment_methods(self, payment):
        # Using 'payment.country' like this assumes that payment is a DocDataPaymentOrder.
        assert isinstance(payment, DocDataPaymentOrder)
        return factory.get_payment_method_ids(amount=payment.amount, currency=payment.currency, country=payment.country,
                                              recurring=payment.order.recurring)

    def get_payment_url(self, payment):
        if payment.payment_method_id:
            # TODO Remove the try/except when 'current' alias is remove. The correct error response should be returned
            #      in the view.
            try:
                return payments.get_payment_url(payment, getattr(settings, "COWRY_RETURN_URL_BASE"))
            except PaymentException as e:
                return None
        return None

    def validate_payment_method(self, attrs, source):
        """
        Check that the payment method is valid for this order / payment.
        """
        value = attrs[source]
        if not value in self.get_available_payment_methods(self.object):
            raise serializers.ValidationError(
                _(u"%(payment_method_id)s is not a valid payment method." % {'payment_method_id': value}))
        return attrs

    class Meta:
        model = Payment
        fields = ('id', 'payment_method', 'payment_submethod', 'available_payment_methods', 'payment_url', 'status')

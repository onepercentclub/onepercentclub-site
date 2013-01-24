from apps.payments.serializers import PaymentMethodSerializer, PaymentSerializer
from cowry.models import PaymentMethod, Payment
from apps.fund.views import CartMixin
from rest_framework import generics
from django.utils import timezone


class CurrentPaymentMixin(CartMixin):

    def get_payment(self):
        # For an anonymous user the order (cart) might be stored in the session
        payment_id = self.request.session.get("payment_id")
        if payment_id:
            try:
                payment = Payment.objects.get(id=payment_id, status=Payment.PaymentStatuses.checkout)
            except Payment.DoesNotExist:
                # The order_id was not a cart in the db, create a new order (cart)
                payment = self.create_payment()
        else:
            # No order_id in session. Create a new order (cart)
            payment = self.create_payment()
        return payment

    def create_payment(self):
        order = self.get_or_create_order()
        payment = Payment(created=timezone.now(), amount=order.amount, status=Payment.PaymentStatuses.checkout)
        if self.request.user.is_authenticated():
            payment.user = self.request.user
        payment.save()
        self.request.session["payment_id"] = order.id
        return payment


class PaymentMethodList(generics.ListAPIView):
    model = PaymentMethod
    serializer_class = PaymentMethodSerializer
    paginate_by = 100


class CurrentPaymentDetail(CurrentPaymentMixin, generics.RetrieveUpdateDestroyAPIView):
    model = Payment
    serializer_class = PaymentSerializer

    def get_object(self):
        return self.get_payment()
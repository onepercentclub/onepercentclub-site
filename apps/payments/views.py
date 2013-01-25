from apps.fund.models import Order
from apps.fund.views import CartMixin
from apps.payments.serializers import PaymentMethodSerializer, PaymentSerializer
from cowry.models import PaymentMethod, Payment
from rest_framework import generics
from django.utils import timezone
from django.utils.translation import ugettext as _



class CurrentPaymentMixin(CartMixin):

    def get_payment(self):
        order = self.get_or_create_order()
        if not order:
            return None
        if order.payment:
            order.payment.amount = order.amount
            return order.payment
        payment = Payment(created=timezone.now(), amount=order.amount, status=Payment.PaymentStatuses.cart)
        if self.request.user.is_authenticated():
            payment.user = self.request.user
        payment.save()
        order.payment = payment
        order.status = Order.OrderStatuses.cart
        order.save()
        return payment


class PaymentMethodList(generics.ListAPIView):
    model = PaymentMethod
    serializer_class = PaymentMethodSerializer
    paginate_by = 100


class CheckoutDetail(CurrentPaymentMixin, generics.RetrieveUpdateDestroyAPIView):
    model = Payment
    serializer_class = PaymentSerializer

    def get_object(self):
        return self.get_payment()


from apps.payments.serializers import PaymentMethodSerializer, PaymentSerializer
from cowry.models import PaymentMethod, Payment
from rest_framework import generics


class CurrentPaymentMixin(object):

    def get_payment(self):
        # see if the user already has a payment (with status 'checkout') in the database
        if self.request.user.is_authenticated():
            try:
                payment = Payment.objects.get(user=self.request.user, status=Payment.PaymentStatuses.checkout)
            except Payment.DoesNotExist:
                # If we can't find a order (cart) for this user create one
                payment = self.create_payment()
        else:
            # For an anonymous user the order (cart) might be stored in the session
            payment_id = self.request.session.get("cowry_payment_id")
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


class PaymentMethodList(generics.ListAPIView):
    model = PaymentMethod
    serializer_class = PaymentMethodSerializer
    paginate_by = 100


class CurrentPaymentDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Payment
    serializer_class = PaymentSerializer

    def get_object(self):
        return CurrentPaymentMixin
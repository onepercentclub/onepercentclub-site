from rest_framework import generics
from rest_framework import response
from rest_framework import status
from . import payments
from .exceptions import PaymentException
from .models import Payment
from .permissions import IsOrderCreator
from .serializers import PaymentSerializer


class PaymentDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    View for working with Payments. Payments can be retrieved (GET), the payment method and submethod can updated (PUT)
    and a payment can be cancelled (DELETE).
    """
    model = Payment
    serializer_class = PaymentSerializer
    permission_classes = (IsOrderCreator,)

    def destroy(self, request, *args, **kwargs):
        payment = self.get_object()
        try:
            payments.cancel_payment(payment)
        except (NotImplementedError, PaymentException) as e:
            return response.Response(data=e, status=status.HTTP_400_BAD_REQUEST)
        else:
            return response.Response(status=status.HTTP_202_ACCEPTED)

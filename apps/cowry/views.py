from rest_framework import generics
from .models import Payment
from .permissions import IsOrderCreator
from .serializers import PaymentSerializer


class PaymentDetail(generics.RetrieveUpdateAPIView):
    """
    View for working with Payments. Payments can be retrieved (GET), the payment method and submethod can updated (PUT)
    and a payment can be cancelled (DELETE).
    """
    model = Payment
    serializer_class = PaymentSerializer
    permission_classes = (IsOrderCreator,)

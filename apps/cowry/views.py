from rest_framework import generics
from .permissions import IsOrderCreator
from .serializers import PaymentSerializer
from .models import Payment


class PaymentDetail(generics.RetrieveUpdateAPIView):
    """
    View for working with Payments. Payments can be retrieved and the payment method and submethod can updated.
    """
    model = Payment
    serializer_class = PaymentSerializer
    permission_classes = (IsOrderCreator,)

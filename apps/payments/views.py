from apps.payments.serializers import PaymentMethodSerializer
from cowry.models import PaymentMethod
from rest_framework import generics


class PaymentMethodList(generics.ListAPIView):
    model = PaymentMethod
    serializer_class = PaymentMethodSerializer
    paginate_by = 100


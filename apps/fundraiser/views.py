from rest_framework import generics

from .models import FundRaiser
from .serializers import FundRaiserSerializer

class FundRaiserListView(generics.ListAPIView):
    model = FundRaiser
    serializer_class = FundRaiserSerializer
    paginate_by = 4

    # TODO: override get_queryset to specify ordering?
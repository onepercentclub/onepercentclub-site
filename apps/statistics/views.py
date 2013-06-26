from rest_framework import generics
from .models import Statistic
from .serializers import StatisticSerializer


# API views

class StatisticDetail(generics.RetrieveAPIView):
    model = Statistic
    serializer_class = StatisticSerializer

    def get_object(self, queryset=None):
        stats = Statistic.objects.get(pk=1)
        return stats


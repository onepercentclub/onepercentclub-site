from rest_framework import generics
from .models import Quote
from .serializers import QuoteSerializer
from django.utils.timezone import now
from django.db.models import Q


# API views

class QuoteList(generics.ListAPIView):
    model = Quote
    serializer_class = QuoteSerializer
    paginate_by = 10
    filter_fields = ('language', 'segment')

    def get_queryset(self):
        qs = super(QuoteList, self).get_queryset()
        qs = qs.filter(status=Quote.QuoteStatus.published)
        qs = qs.filter(publication_date__lte=now)
        qs = qs.filter(Q(publication_end_date__gte=now) | Q(publication_end_date__isnull=True))
        return qs


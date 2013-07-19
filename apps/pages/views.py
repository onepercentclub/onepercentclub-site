from apps.pages.models import ContactMessage
from apps.pages.serializers import ContactMessageSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import Http404
from rest_framework import generics
from .models import Page
from .serializers import PageSerializer
from django.utils.timezone import now
from django.db.models import Q
from django.utils.translation import ugettext as _



class PageList(generics.ListAPIView):
    model = Page
    serializer_class = PageSerializer
    paginate_by = 10
    filter_fields = ('language', 'slug')

    def get_queryset(self):
        qs = super(PageList, self).get_queryset()
        qs = qs.filter(status=Page.PageStatus.published)
        qs = qs.filter(publication_date__lte=now)
        qs = qs.filter(Q(publication_end_date__gte=now) | Q(publication_end_date__isnull=True))
        return qs


class PageDetail(generics.RetrieveAPIView):
    model = Page
    serializer_class = PageSerializer

    def get_queryset(self):
        qs = super(PageDetail, self).get_queryset()
        qs = qs.filter(status=Page.PageStatus.published)
        qs = qs.filter(publication_date__lte=now)
        qs = qs.filter(Q(publication_end_date__gte=now) | Q(publication_end_date__isnull=True))
        return qs

    def get_object(self, queryset=None):
        qs = self.get_queryset()
        qs = qs.filter(slug=self.kwargs['slug'])
        qs = qs.filter(language=self.kwargs['language'])
        try:
            # Get the single item from the filtered queryset
            obj = qs.get()
        except ObjectDoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj


class ContactRequestCreate(generics.CreateAPIView):
    model = ContactMessage
    serializer_class = ContactMessageSerializer

    def pre_save(self, obj):
        if self.request.user.is_authenticated():
            obj.author = self.request.user

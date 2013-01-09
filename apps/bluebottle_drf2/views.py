from rest_framework import generics
from django.utils import timezone
from rest_framework import response
from rest_framework import status


class SoftDeleteModelMixin(object):
    """
    This Mixin marks an object as deleted by setting the deleted field to the current time.
    """
    def destroy(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.deleted = timezone.now()
        self.object.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class NonDeletedModelMixin(object):
    """
    Filter the queryset to only show non-deleted items
    """

    def get_queryset(self, queryset=None):
        queryset = super(NonDeletedModelMixin, self).get_queryset()
        queryset = queryset.filter(deleted__isnull=True)
        return queryset


class RetrieveAPIView(NonDeletedModelMixin, generics.RetrieveAPIView):
    pass


class DeleteAPIView(SoftDeleteModelMixin, NonDeletedModelMixin, generics.DestroyAPIView):
    pass


class RetrieveDeleteAPIView(SoftDeleteModelMixin, NonDeletedModelMixin, generics.RetrieveDestroyAPIView):
    pass


class RetrieveUpdateDeleteAPIView(SoftDeleteModelMixin, NonDeletedModelMixin, generics.RetrieveUpdateDestroyAPIView):
    pass


class ListAPIView(NonDeletedModelMixin, generics.ListAPIView):
    pass


class ListCreateAPIView(NonDeletedModelMixin, generics.ListCreateAPIView):
    pass



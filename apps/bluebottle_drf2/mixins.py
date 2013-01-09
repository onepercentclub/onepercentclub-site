from django.utils.timezone import datetime
from rest_framework import response
from rest_framework import status

class SoftDeleteModelMixin(object):
    """
    Mark an object as deleted
    This Mixin marks an object as deleted by setting the deleted field to the current time. This should be mixed in with a
    SingleObjectBaseView and needs to precede a generics.RetrieveDestroyAPIView in the class definition.

    When using this mixin the queryset should be filtered on 'deleted' property like:
    objects = objects.filter(deleted__isnull = True)
    """
    def destroy(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.deleted = datetime.now()
        self.object.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


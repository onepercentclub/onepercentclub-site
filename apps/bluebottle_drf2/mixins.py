from datetime import datetime
from rest_framework import response
from rest_framework import status

class SoftDeleteModelMixin(object):
    """
    Mark an object as deleted
    Should be mixed in with `SingleObjectBaseView`.
    Should precede a generics.RetrieveDestroyAPIView in class definition.
    """
    def destroy(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.deleted = datetime.now()
        self.object.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


from rest_framework import generics
from .serializers import MediaWallPostSerializer
from .models import WallPost
from django.contrib.contenttypes.models import ContentType

class WallPostList(generics.ListAPIView):
    model = WallPost
    serializer_class = MediaWallPostSerializer
    paginate_by = 10


    def get_queryset(self):
        """
        Filter wallposts for the current object
        """
        queryset = WallPost.objects.all()
        print self.kwargs
        object_type = ContentType.objects.get_for_id(self.kwargs.get('content_type'))

        if self.kwargs.get('slug'):
            object = object_type.get_object_for_this_type(slug=self.kwargs.get('slug'))
            id = object.id
        else:
            id = self.kwargs.get('id')

        queryset = queryset.filter(content_type=self.kwargs.get('content_type'))
        queryset = queryset.filter(object_id=id)
        return queryset



class WallPostDetail(generics.RetrieveAPIView):
    model = WallPost
    serializer_class = MediaWallPostSerializer



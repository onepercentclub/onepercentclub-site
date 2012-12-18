from django.contrib.contenttypes.models import ContentType
from rest_framework import generics
from .serializers import WallPostSerializer
from .models import WallPost


class WallPostList(generics.ListAPIView):
    model = WallPost
    serializer_class = WallPostSerializer
    paginate_by = 10

    def _get_wallposts_for_instance(self):
        reaction_to_type = ContentType.objects.get_for_id(self.kwargs['content_type'])
        return reaction_to_type.get_object_for_this_type(slug=self.kwargs['slug'])

    def get_queryset(self):
        reaction_to_instance = self._get_wallposts_for_instance()
        objects = self.model.objects.for_content_type(self.kwargs['content_type'])
        objects = objects.order_by("-created")
        return objects.filter(object_id=reaction_to_instance.id)




class WallPostDetail(generics.RetrieveAPIView):
    model = WallPost
    serializer_class = WallPostSerializer



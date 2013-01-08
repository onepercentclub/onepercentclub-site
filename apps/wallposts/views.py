from rest_framework import generics
from apps.bluebottle_utils.utils import get_client_ip
from .serializers import WallPostSerializer, TextWallPostSerializer, MediaWallPostSerializer
from apps.bluebottle_drf2.mixins import SoftDeleteModelMixin
from .models import WallPost, MediaWallPost, TextWallPost


class WallPostList(generics.ListCreateAPIView):
    # Please extend this in specific app. We probably don't want to use this directly.
    model = WallPost
    serializer_class = WallPostSerializer
    paginate_by = 10

    def get_content_type(self):
        # Have a separate function for this so we can easily override it for specific WallPost APIs.
        return self.request.QUERY_PARAMS.get('content_type', None)

    def get_object_id(self):
        return self.request.QUERY_PARAMS.get('object_id', None)

    def get_queryset(self):
        objects = self.model.objects
        if self.get_content_type():
            objects = objects.for_content_type(self.get_content_type())
        if self.get_object_id():
            # TODO: We should really throw a warning if content_type is not set here.
            objects = objects.filter(object_id=self.get_object_id())
        objects = objects.filter(deleted__isnull = True)
        objects = objects.order_by("-created")
        return objects

    def pre_save(self, obj):
        obj.author = self.request.user
        obj.ip_address = get_client_ip(self.request)


class WallPostDetail(SoftDeleteModelMixin, generics.RetrieveDestroyAPIView):
    # Please extend this in specific app. We probably don't want to use this directly.
    model = WallPost
    serializer_class = WallPostSerializer


class MediaWallPostDetail(WallPostDetail):
    model = MediaWallPost
    serializer_class = MediaWallPostSerializer


class TextWallPostDetail(WallPostDetail):
    model = TextWallPost
    serializer_class = TextWallPostSerializer


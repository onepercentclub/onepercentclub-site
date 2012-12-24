from django.contrib.contenttypes.models import ContentType
from rest_framework import generics
from apps.projects.models import Project
from .serializers import WallPostSerializer
from .models import WallPost


class WallPostList(generics.ListAPIView):
    model = WallPost
    serializer_class = WallPostSerializer
    paginate_by = 10

    def get_content_type(self):
        # Have a separate function for this so we can easily
        # overwrite it for specific wallpost APIs
        return self.request.QUERY_PARAMS.get('content_type', None)

    def get_object_id(self):
        return self.request.QUERY_PARAMS.get('object_id', None)

    def get_queryset(self):
        objects = self.model.objects
        if self.get_content_type():
            objects = objects.for_content_type(self.get_content_type())
        if self.get_object_id():
            # TODO: We should throw realy a warning if content_type is not set here
            objects = objects.filter(object_id=self.get_object_id())
        objects = objects.order_by("-created")
        return objects


class WallPostDetail(generics.RetrieveAPIView):
    model = WallPost
    serializer_class = WallPostSerializer


class ProjectWallPostList(WallPostList):

    def get_content_type(self):
        ct = ContentType.objects.get_for_model(Project)
        return ct.id

    def get_object_id(self):
        # We want to specific and use project_id here 
        return self.request.QUERY_PARAMS.get('project_id', None)



class ProjectWallPostDetail(WallPostDetail):
    # We don't need to set the content_type and project_id for this
    # resource, because wallposts will be unique across different wp types 
    pass



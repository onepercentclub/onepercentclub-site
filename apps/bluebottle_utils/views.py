from apps.bluebottle_utils.serializers import ThemeSerializer
from apps.projects.models import ProjectTheme
from rest_framework import generics
from rest_framework import views, response
from taggit.models import Tag


class ThemeList(generics.ListAPIView):
    model = ProjectTheme
    serializer_class = ThemeSerializer


class TagList(views.APIView):
    """
    All tags in use on this system
    """

    def get(self, request, format=None):

        data = [tag.name for tag in Tag.objects.filter(name__contains='man').all()[:20]]
        return response.Response(data)
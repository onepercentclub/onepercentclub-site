from apps.homepage.model import HomePage
from rest_framework import generics, response
from .serializers import HomePageSerializer


# Instead of serving all the objects separately we combine Slide, Quote and Stats into a dummy object
class HomePageDetail(generics.GenericAPIView):
    serializer_class = HomePageSerializer

    def get(self, request, language='en'):
        homepage = HomePage().get(language)
        serialized = HomePageSerializer().to_native(homepage)
        return response.Response(serialized)



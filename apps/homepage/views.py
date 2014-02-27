from rest_framework import generics, response

from .models import HomePage
from .serializers import HomePageSerializer


# Instead of serving all the objects separately we combine Slide, Quote and Stats into a dummy object
class HomePageDetail(generics.GenericAPIView):
    serializer_class = HomePageSerializer

    def get(self, request, language='en'):
        homepage = HomePage().get(language)
        serialized = HomePageSerializer().to_native(homepage)
        return response.Response(serialized)



from apps.accounts.serializers import UserPreviewSerializer
from apps.bluebottle_drf2.serializers import SorlImageField
from fluent_contents.rendering import render_placeholder
from rest_framework import serializers
from .models import Slide



class SlideSerializer(serializers.ModelSerializer):
    author = UserPreviewSerializer()
    image = SorlImageField('image', '247x180', crop='center')

    class Meta:
        model = Slide
        #fields = ('title', 'contents', 'language', 'sequence')

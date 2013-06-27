from apps.accounts.serializers import UserPreviewSerializer
from fluent_contents.rendering import render_placeholder
from rest_framework import serializers
from .models import Slide



class SlideSerializer(serializers.ModelSerializer):
    author = UserPreviewSerializer()

    class Meta:
        model = Slide
        #fields = ('title', 'contents', 'language', 'sequence')

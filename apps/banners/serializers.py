from apps.accounts.serializers import UserPreviewSerializer
from fluent_contents.rendering import render_placeholder
from rest_framework import serializers
from .models import Slide


class SlideContentsField(serializers.Field):

    def to_native(self, obj):
        request = self.context.get('request', None)
        contents_html = render_placeholder(request, obj)
        return contents_html


class SlideSerializer(serializers.ModelSerializer):
    contents = SlideContentsField(source='contents')
    author = UserPreviewSerializer()

    class Meta:
        model = Slide
        fields = ('title', 'contents', 'language', 'sequence')

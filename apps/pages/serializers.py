from apps.accounts.serializers import UserPreviewSerializer
from fluent_contents.rendering import render_placeholder
from rest_framework import serializers
from .models import Page


class PageContentsField(serializers.Field):

    def to_native(self, obj):
        request = self.context.get('request', None)
        contents_html = render_placeholder(request, obj)
        return contents_html


class PageSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='slug', read_only=True)
    body = PageContentsField(source='body')
    author = UserPreviewSerializer()

    class Meta:
        model = Page
        fields = ('title', 'id', 'body', 'language')

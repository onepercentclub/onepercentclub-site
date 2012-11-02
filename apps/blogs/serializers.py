from fluent_contents.rendering import render_placeholder
from rest_framework import serializers
from .models import BlogPost


class BlogPostContentsField(serializers.Field):

    def to_native(self, obj):
        request = self.context.get('request', None)
        contents_html = render_placeholder(request, obj)
        return contents_html


class BlogPostDetailSerializer(serializers.ModelSerializer):
    contents = BlogPostContentsField('contents')

    class Meta:
        model = BlogPost


class BlogPostPreviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = BlogPost

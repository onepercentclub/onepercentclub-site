from bluebottle.accounts.serializers import UserPreviewSerializer
from fluent_contents.rendering import render_placeholder
from rest_framework import serializers
from bluebottle.bluebottle_drf2.serializers import SorlImageField
from .models import BlogPost


class BlogPostContentsField(serializers.Field):

    def to_native(self, obj):
        request = self.context.get('request', None)
        contents_html = render_placeholder(request, obj)
        return contents_html


class BlogPostSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='slug')
    body = BlogPostContentsField(source='contents')
    main_image = SorlImageField('main_image', '300x200',)
    author = UserPreviewSerializer()

    class Meta:
        model = BlogPost
        fields = ('id', 'title', 'body', 'main_image', 'author', 'publication_date', 'allow_comments', 'post_type', 'language')


class BlogPostPreviewSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='slug')

    class Meta:
        model = BlogPost
        fields = ('id', 'title', 'publication_date')


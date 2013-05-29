from apps.accounts.serializers import UserPreviewSerializer
from fluent_contents.rendering import render_placeholder
from rest_framework import serializers
from apps.bluebottle_drf2.serializers import SorlImageField
from .models import BlogPost


class BlogPostContentsField(serializers.Field):

    def to_native(self, obj):
        request = self.context.get('request', None)
        contents_html = render_placeholder(request, obj)
        return contents_html


class BlogPostDetailSerializer(serializers.ModelSerializer):
    contents = BlogPostContentsField(source='contents')
    url = serializers.HyperlinkedIdentityField(view_name='blogpost-instance')
    main_image = SorlImageField('main_image', '300x200',)
    author = UserPreviewSerializer()

    class Meta:
        model = BlogPost
        exclude = ('id',)


class BlogPostPreviewSerializer(BlogPostDetailSerializer):

    class Meta:
        model = BlogPost
        exclude = ('id',)

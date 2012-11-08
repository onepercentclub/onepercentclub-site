from apps.bluebottle_utils.serializers import SorlImageField, SlugHyperlinkedIdentityField
from django.contrib.auth.models import User
from fluent_contents.rendering import render_placeholder
from rest_framework import serializers
from .models import BlogPost


class BlogPostContentsField(serializers.Field):

    def to_native(self, obj):
        request = self.context.get('request', None)
        contents_html = render_placeholder(request, obj)
        return contents_html


class BlogPostAuthorSerializer(serializers.ModelSerializer):
    picture = SorlImageField('userprofile.picture', '90x90', crop='center')

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'picture')


class BlogPostDetailSerializer(serializers.ModelSerializer):
    contents = BlogPostContentsField(source='contents')
#   TODO: Enable embedded models in Ember Data and re-enable this.
#    author = BlogPostAuthorSerializer()
    url = SlugHyperlinkedIdentityField(view_name='blogpost-instance')
    main_image = SorlImageField('main_image', '300x200', crop='center')

    class Meta:
        model = BlogPost
        exclude = ('id',)

class BlogPostPreviewSerializer(BlogPostDetailSerializer):

    class Meta:
        model = BlogPost
        exclude = ('id',)

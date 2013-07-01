from apps.blogs.views import BlogPostList, BlogPostDetail
from apps.bluebottle_utils.tests import UserTestsMixin, generate_random_slug
from django.test import TestCase
from django.utils.timezone import now
from rest_framework import status
from apps.blogs.models import BlogPostProxy
from fluent_contents.models import Placeholder



class BlogPostCreationMixin(UserTestsMixin):

    def create_blogpost(self, title='We make it work', slug=None, language='nl', user=None, post_type='news',
                        status='published', published_date=now()):
        bp = BlogPostProxy()

        if not slug:
            slug = generate_random_slug()
            # Ensure generated slug is unique.
            while BlogPostProxy.objects.filter(slug=slug).exists():
                slug = generate_random_slug()

        if not user:
            user = self.create_user()
            user.save()

        bp.title = title
        bp.status = status
        bp.published_date = published_date
        bp.post_type = post_type
        bp.title = title
        bp.slug = slug
        bp.author = user
        bp.save()

        # The contents needs to be created separately.
        ph = Placeholder.objects.create_for_object(bp, 'blog_contents')
        ph.save()

        return bp


class BlogPostApiIntegrationTest(BlogPostCreationMixin, TestCase):
    """
    Integration tests for the BlogPost API.
    """

    def setUp(self):
        self.post = self.create_blogpost()
        self.list_view = BlogPostList.as_view()
        self.detail_view = BlogPostDetail.as_view()
        self.post_url = "{0}{1}".format('/i18n/api/blogs/', self.post.slug)


    def test_blog_post_retrieve(self):
        """
        Test retrieving a BlogPost.
        """

        # Retrieve reaction.
        response = self.client.get(self.post_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['title'], self.post.title)

from apps.blogs.views import BlogPostList, BlogPostDetail
from apps.bluebottle_utils.tests import BlogPostCreationMixin
from django.test import TestCase
from rest_framework import status


class BlogPostApiIntegrationTest(BlogPostCreationMixin, TestCase):
    """
    Integration tests for the BlogPost API.
    """

    def setUp(self):
        self.blogpost = self.create_blogpost()
        self.list_view = BlogPostList.as_view()
        self.detail_view = BlogPostDetail.as_view()
        self.blogpost_detail_url = "{0}{1}".format('/i18n/api/blogs/', self.blogpost.slug)


    def test_blogpost_retrieve(self):
        """
        Test retrieving a BlogPost.
        """

        # Retrieve reaction.
        response = self.client.get(self.blogpost_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['title'], self.blogpost.title)

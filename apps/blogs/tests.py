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
        bp.language = language
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
        self.some_dutch_news = self.create_blogpost(post_type='news', language='nl')
        self.some_other_dutch_news = self.create_blogpost(post_type='news', language='nl')
        self.third_dutch_news = self.create_blogpost(post_type='news', language='nl')

        self.some_dutch_blog = self.create_blogpost(post_type='blog', language='nl')
        self.some_other_dutch_blog = self.create_blogpost(post_type='blog', language='nl')

        # next_weeh = now().
        # self.some_future_dutch_blog = self.create_blogpost(post_type='blog', language='nl', )

        self.some_english_news = self.create_blogpost(post_type='news', language='nl')
        self.some_other_english_news = self.create_blogpost(post_type='news', language='nl')
        self.some_unpublished_english_news = self.create_blogpost(post_type='news', language='nl', published=False)

        self.some_english_blog = self.create_blogpost(post_type='blog', language='en')

        self.blog_url =  '/i18n/api/blogs/'

    def test_news_retrieve(self):
        """
        Test retrieving a news item.
        """

        # Check that we have 3 dutch news items
        response = self.client.get(self.blog_url, {'post_type': 'news', 'language': 'nl'})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['count'], 3)

        # Retrieve first news items.
        post_url = "{0}{1}".format(self.blog_url, self.some_dutch_news.slug)
        response = self.client.get(self.post_url, {'post_type': 'news', 'language': 'nl'})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['title'], self.some_dutch_news.title)

        # Check that we have 2 english news items
        response = self.client.get(self.blog_url, {'post_type': 'news', 'language': 'nl'})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['count'], 2)

        # Check that we have 2 dutch blog items
        response = self.client.get(self.blog_url, {'post_type': 'blog', 'language': 'nl'})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['count'], 3)



from bluebottle.bluebottle_utils.tests import UserTestsMixin, generate_random_slug
from django.test import TestCase
from django.utils.timezone import now
from rest_framework import status
from apps.blogs.models import NewsPostProxy, BlogPostProxy
from fluent_contents.models import Placeholder


class BlogPostCreationMixin(UserTestsMixin):

    def create_news_post(self, title='We make it work', slug=None, language='nl', user=None, status='published',
                        published_date=now()):
        post = NewsPostProxy()

        if not slug:
            slug = generate_random_slug()
            # Ensure generated slug is unique.
            while NewsPostProxy.objects.filter(slug=slug).exists():
                slug = generate_random_slug()

        if not user:
            user = self.create_user()
            user.save()

        post.title = title
        post.status = status
        post.published_date = published_date
        post.language = language
        post.title = title
        post.slug = slug
        post.author = user
        post.save()

        # The contents needs to be created separately.
        ph = Placeholder.objects.create_for_object(post, 'blog_contents')
        ph.save()

        return post


    def create_blog_post(self, title='We make it work', slug=None, language='nl', user=None, status='published',
                        published_date=now()):
        post = BlogPostProxy()

        if not slug:
            slug = generate_random_slug()
            # Ensure generated slug is unique.
            while BlogPostProxy.objects.filter(slug=slug).exists():
                slug = generate_random_slug()

        if not user:
            user = self.create_user()
            user.save()

        post.title = title
        post.status = status
        post.published_date = published_date
        post.language = language
        post.title = title
        post.slug = slug
        post.author = user
        post.save()

        # The contents needs to be created separately.
        ph = Placeholder.objects.create_for_object(post, 'blog_contents')
        ph.save()

        return post


class BlogPostApiIntegrationTest(BlogPostCreationMixin, TestCase):
    """
    Integration tests for the BlogPost API.
    """

    def setUp(self):
        self.some_dutch_news = self.create_news_post(language='nl')
        self.some_other_dutch_news = self.create_news_post(language='nl')
        self.third_dutch_news = self.create_news_post(language='nl')

        self.some_dutch_blog = self.create_blog_post(language='nl')
        self.some_other_dutch_blog = self.create_blog_post(language='nl')

        self.some_english_news = self.create_news_post(language='en')
        self.some_other_english_news = self.create_news_post(language='en')
        self.some_unpublished_english_news = self.create_news_post(language='en', status='draft')

        self.some_english_blog = self.create_blog_post(language='en')

        self.news_url = '/api/blogs/news/'
        self.blog_url = '/api/blogs/posts/'


    def test_news_retrieve(self):
        """
        Test retrieving a news item.
        """

        # Check that we have 3 dutch news items
        #response = self.client.get(self.blog_url)

        response = self.client.get(self.news_url, {'language': 'nl'})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['count'], 3, response.data)

        # Retrieve first news items.
        post_url = "{0}{1}".format(self.news_url, self.some_dutch_news.slug)
        response = self.client.get(post_url, {'language': 'nl'})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['title'], self.some_dutch_news.title)

        # Check that we have 2 english news items
        response = self.client.get(self.news_url, {'language': 'en'})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['count'], 2)

        # Check that we have 2 dutch blog items
        response = self.client.get(self.blog_url, {'language': 'nl'})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['count'], 2)



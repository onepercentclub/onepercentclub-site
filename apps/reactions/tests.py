from apps.blogs.models import BlogPost
from apps.blogs.views import BlogPostList, BlogPostDetail
from apps.bluebottle_utils.tests import UserTestsMixin, generate_slug
from django.test import TestCase
from rest_framework import status
from rest_framework.tests.authentication import Client


class BlogPostCreationMixin(UserTestsMixin):

    def create_blogpost(self, title=None, slug=None, language=None, user=None):
        bp = BlogPost()

        if not title:
            title = 'We Make it Work!'

        if not slug:
            slug = generate_slug()
            # Ensure generated slug is unique.
            while BlogPost.objects.filter(slug=slug).exists():
                slug = generate_slug()

        if not language:
            language = 'nl'

        if not user:
            user = self.create_user()
            user.save()

        bp.title = title
        bp.language = language
        bp.slug = slug
        bp.author = user
        bp.save()

        return bp


class ReactionApiIntegrationTest(BlogPostCreationMixin, TestCase):
    """
    Integration tests for the BlogPost API.
    """

    def setUp(self):
        # TODO: Add a test for reaction on another type of content.
        self.blogpost1 = self.create_blogpost()

        self.list_view = BlogPostList.as_view()
        self.detail_view = BlogPostDetail.as_view()
        self.api_base = '/i18n/api/blogs/'
        self.reaction_api_name = '/reactions/'

        self.client = Client(enforce_csrf_checks=False)
        self.client.login(username=self.blogpost1.author.username, password='password')

    def tearDown(self):
        self.client.logout()

    def test_create_and_retrieve_reaction(self):
        """
        Basic test for creating and retrieving a reaction.
        """
        reaction_text = 'Great job!'
        response = self.client.post(self.api_base + self.blogpost1.slug + self.reaction_api_name, {'reaction': reaction_text})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reaction'], reaction_text)

        id = response.data['id']
        response = self.client.get(self.api_base + self.blogpost1.slug + self.reaction_api_name + str(id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reaction'], reaction_text)

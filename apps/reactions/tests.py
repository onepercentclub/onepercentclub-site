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
    Integration tests for the Reaction API.
    """
    # TODO: Add a test for reaction on another type of content.

    def setUp(self):
        self.blogpost = self.create_blogpost()
        self.list_view = BlogPostList.as_view()
        self.detail_view = BlogPostDetail.as_view()
        self.api_base = '/i18n/api/blogs/'
        self.reaction_api_name = '/reactions/'
        self.reactions_url = self.api_base + self.blogpost.slug + self.reaction_api_name

        self.client = Client(enforce_csrf_checks=False)
        self.client.login(username=self.blogpost.author.username, password='password')

    def tearDown(self):
        self.client.logout()

    def test_reaction_crud(self):
        """
        Tests for creating, retrieving, updating and deleting a reaction.
        """

        # Create reaction.
        reaction_text = 'Great job!'
        response = self.client.post(self.reactions_url, {'reaction': reaction_text})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reaction'], reaction_text)

        # Retrieve reaction.
        reaction_detail_url = self.reactions_url + str(response.data['id'])
        response = self.client.get(reaction_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reaction'], reaction_text)

        # Update reaction.
        new_reaction_text = 'This is a really nice post.'
        response = self.client.put(reaction_detail_url, {'reaction': new_reaction_text})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reaction'], new_reaction_text)

        # Delete reaction.
        response = self.client.delete(reaction_detail_url, {'reaction': new_reaction_text})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


    def test_reactions_on_multiple_objects(self):
        """
        Tests for multiple reactions and unauthorized reaction updates.
        """

        # Create two reactions.
        reaction_text_1 = 'Great job!'
        response = self.client.post(self.reactions_url, {'reaction': reaction_text_1})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reaction'], reaction_text_1)

        reaction_text_2 = 'This is a really nice post.'
        response = self.client.post(self.reactions_url, {'reaction': reaction_text_2})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reaction'], reaction_text_2)

        # Check the size of the reaction list is correct.
        response = self.client.get(self.reactions_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

        # Create a reaction on second blog post.
        second_blogpost = self.create_blogpost(title='Ben Jij Rijk?')
        second_reactions_url = self.api_base + second_blogpost.slug + self.reaction_api_name
        reaction_text_3 = 'Super!'
        response = self.client.post(second_reactions_url, {'reaction': reaction_text_3})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reaction'], reaction_text_3)

        # Check that the size and data in the first reaction list is correct.
        response = self.client.get(self.reactions_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['reaction'], reaction_text_1)
        self.assertEqual(response.data['results'][1]['reaction'], reaction_text_2)

        # Check that the size and data in the second reaction list is correct.
        response = self.client.get(second_reactions_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['reaction'], reaction_text_3)

        # Test that a reaction update from a user who is not the author is forbidden.
        client2 = Client(enforce_csrf_checks=False)
        client2.login(username=second_blogpost.author.username, password='password')
        response = client2.get(self.reactions_url)
        response = client2.post(self.reactions_url + str(response.data['results'][0]['id']), {'reaction': 'Can I update this reaction?'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

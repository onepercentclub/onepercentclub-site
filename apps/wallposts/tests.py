from apps.projects.tests import ProjectTestsMixin
from apps.wallposts.models import TextWallPost
from django.test import TestCase
from rest_framework import status

class WallPostMixin(ProjectTestsMixin):
    """ Mixin base class for tests using wallposts. """

    def create_project_text_wallpost(self, text='Some smart comment.', project=None, author=None):
        if not project:
            project = self.create_project()
        if not author:
            author = self.create_user()

        wallpost = TextWallPost.objects.create()
        wallpost.content_object = project
        wallpost.author = author
        wallpost.text = text
        wallpost.save()
        return wallpost



class WallPostReactionApiIntegrationTest(WallPostMixin, TestCase):
    """
    Integration tests for the Project Media WallPost API.
    """

    def setUp(self):
        self.some_wallpost = self.create_project_text_wallpost()
        self.another_wallpost = self.create_project_text_wallpost()
        self.some_user = self.create_user()
        self.another_user = self.create_user()
        self.wallpost_reaction_url = '/i18n/api/wallposts/reactions/'


    def test_wallpost_reaction_crud(self):
        """
        Tests for creating, retrieving, updating and deleting a reaction to a Project WallPost.
        """

        # Create a Reaction
        reaction_text = "Hear! Hear!"
        self.client.login(username=self.some_user.username, password='password')
        response = self.client.post(self.wallpost_reaction_url, {'reaction': reaction_text, 'wallpost_id': self.some_wallpost.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['reaction'], reaction_text)

        # Retrieve the created Reaction
        reaction_detail_url = "{0}{1}".format(self.wallpost_reaction_url, str(response.data['id']))
        response = self.client.get(reaction_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['reaction'], reaction_text)

        # Update the created Reaction by author.
        new_reaction_text = 'HEAR!!! HEAR!!!'
        response = self.client.post(self.wallpost_reaction_url, {'reaction': new_reaction_text, 'wallpost_id': self.some_wallpost.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['reaction'], new_reaction_text)

        # Delete Project Media WallPost by author
        response = self.client.delete(reaction_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response)

        # Retrieve the deleted Reaction should fail
        reaction_detail_url = "{0}{1}".format(self.wallpost_reaction_url, str(response.data['id']))
        response = self.client.get(reaction_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)


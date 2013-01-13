from apps.projects.models import Project
from apps.projects.tests import ProjectTestsMixin
from apps.wallposts.models import TextWallPost, WallPost
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from rest_framework import status

class WallPostMixin(ProjectTestsMixin):
    """ Mixin base class for tests using wallposts. """

    def create_project_text_wallpost(self, text='Some smart comment.', project=None, author=None):
        if not project:
            project = self.create_project()
        if not author:
            author = self.create_user()
        content_type = ContentType.objects.get_for_model(Project)
        wallpost = WallPost.objects.create(
                    content_type = content_type,
                    object_id = project.id
                )
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
        self.client.login(username=self.some_user.username, password='password')
        reaction_text = "Hear! Hear!"
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
        response = self.client.put(reaction_detail_url, {'reaction': new_reaction_text, 'wallpost_id': self.some_wallpost.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['reaction'], new_reaction_text)


        # switch to another user
        self.client.logout()
        self.client.login(username=self.another_user.username, password='password')

        # Retrieve the created Reaction by non-author should work
        reaction_detail_url = "{0}{1}".format(self.wallpost_reaction_url, str(response.data['id']))
        response = self.client.get(reaction_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['reaction'], new_reaction_text)

        # Create a Reaction by another user
        self.client.login(username=self.some_user.username, password='password')
        another_reaction_text = "I'm not so sure..."
        response = self.client.post(self.wallpost_reaction_url, {'reaction': another_reaction_text, 'wallpost_id': self.some_wallpost.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['reaction'], another_reaction_text)


        # Delete Reaction by non-author should not work
        response = self.client.delete(reaction_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response)

        # retrieve the list of Reactions for this WallPost should return two
        response = self.client.get(self.wallpost_reaction_url, {'wallpost_id': self.some_wallpost.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['reaction'], another_reaction_text)
        self.assertEqual(response.data['results'][1]['reaction'], new_reaction_text)


        # back to the author
        self.client.logout()
        self.client.login(username=self.some_user.username, password='password')

        # Delete Reaction by author should work
        response = self.client.delete(reaction_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response)

        # Retrieve the deleted Reaction should fail
        response = self.client.get(reaction_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)


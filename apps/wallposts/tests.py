from apps.projects.models import Project
from apps.projects.tests import ProjectTestsMixin
from apps.wallposts.models import TextWallPost, WallPost
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from rest_framework import status

class ProjectWallPostMixin(ProjectTestsMixin):
    """ Mixin base class for tests using wallposts. """

    def create_project_text_wallpost(self, text='Some smart comment.', project=None, author=None):
        if not project:
            project = self.create_project()
        if not author:
            author = self.create_user()
        content_type = ContentType.objects.get_for_model(Project)
        wallpost = TextWallPost.objects.create(
                    content_type = content_type,
                    object_id = project.id
                )
        wallpost.author = author
        wallpost.text = text
        wallpost.save()
        return wallpost



class WallPostReactionApiIntegrationTest(ProjectWallPostMixin, TestCase):
    """
    Integration tests for the Project Media WallPost API.
    """

    def setUp(self):
        self.some_wallpost = self.create_project_text_wallpost()
        self.another_wallpost = self.create_project_text_wallpost()
        self.some_user = self.create_user()
        self.another_user = self.create_user()
        self.wallpost_reaction_url = '/i18n/api/wallposts/reactions/'
        self.project_text_wallpost_url = '/i18n/api/projects/wallposts/text/'


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
        reaction_detail_url = response.data['url']
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
        response = self.client.get(reaction_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['reaction'], new_reaction_text)

        # Delete Reaction by non-author should not work
        self.client.logout()
        self.client.login(username=self.another_user.username, password='password')
        response = self.client.delete(reaction_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response)

        # Create a Reaction by another user
        another_reaction_text = "I'm not so sure..."
        response = self.client.post(self.wallpost_reaction_url, {'reaction': another_reaction_text, 'wallpost_id': self.some_wallpost.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['reaction'], another_reaction_text)

        # retrieve the list of Reactions for this WallPost should return two
        response = self.client.get(self.wallpost_reaction_url, {'wallpost_id': self.some_wallpost.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['reaction'], new_reaction_text)
        self.assertEqual(response.data['results'][1]['reaction'], another_reaction_text)

        # back to the author
        self.client.logout()
        self.client.login(username=self.some_user.username, password='password')

        # Delete Reaction by author should work
        response = self.client.delete(reaction_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response)

        # Retrieve the deleted Reaction should fail
        response = self.client.get(reaction_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)


    def test_reactions_on_multiple_objects(self):
        """
        Tests for multiple reactions and unauthorized reaction updates.
        """
    
        # Create two reactions.
        self.client.login(username=self.some_user.username, password='password')
        reaction_text_1 = 'Great job!'
        response = self.client.post(self.wallpost_reaction_url, {'reaction': reaction_text_1, 'wallpost_id': self.some_wallpost.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['reaction'], reaction_text_1)
    
        reaction_text_2 = 'This is a really nice post.'
        response = self.client.post(self.wallpost_reaction_url, {'reaction': reaction_text_2, 'wallpost_id': self.some_wallpost.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['reaction'], reaction_text_2)
    
        # Check the size of the reaction list is correct.
        response = self.client.get(self.wallpost_reaction_url, {'wallpost_id': self.some_wallpost.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['count'], 2)
    
        # Create a reaction on second blog post.
        reaction_text_3 = 'Super!'
        response = self.client.post(self.wallpost_reaction_url, {'reaction': reaction_text_3, 'wallpost_id': self.another_wallpost.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['reaction'], reaction_text_3)
        # Save the detail url to be used in the authorization test below.
        second_reaction_detail_url = "{0}{1}".format(self.wallpost_reaction_url, response.data['id'])
    
        # Check that the size and data in the first reaction list is correct.
        response = self.client.get(self.wallpost_reaction_url, {'wallpost_id': self.some_wallpost.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['reaction'], reaction_text_1)
        self.assertEqual(response.data['results'][1]['reaction'], reaction_text_2)
    
        # Check that the size and data in the second reaction list is correct.
        response = self.client.get(self.wallpost_reaction_url, {'wallpost_id': self.another_wallpost.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['reaction'], reaction_text_3)
    
        # Test that a reaction update from a user who is not the author is forbidden.
        self.client.logout()
        self.client.login(username=self.another_user.username, password='password')
        response = self.client.post(second_reaction_detail_url, {'reaction': 'Can I update this reaction?'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED, response.data)


    def test_embedded_reactions(self):
        """
            Test reactions embedded in Project WallPost Api calls
        """

        # Create two Reactions and retrieve the related Project Text WallPost should have the embedded
        self.client.login(username=self.some_user.username, password='password')
        reaction1_text = "Hear! Hear!"
        response = self.client.post(self.wallpost_reaction_url, {'reaction': reaction1_text, 'wallpost_id': self.some_wallpost.id})
        reaction1_detail_url = response.data['url']
        reaction2_text = "This is cool!"
        self.client.post(self.wallpost_reaction_url, {'reaction': reaction2_text, 'wallpost_id': self.some_wallpost.id})
        some_wallpost_detail_url = "{0}{1}".format(self.project_text_wallpost_url, str(self.some_wallpost.id))
        response = self.client.get(some_wallpost_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data['reactions']), 2)
        self.assertEqual(response.data['reactions'][0]['reaction'], reaction1_text)
        self.assertEqual(response.data['reactions'][1]['reaction'], reaction2_text)


        # Create a Reaction to another WallPost and retrieve that WallPost should return one embedded reaction
        reaction3_text = "That other post was way better..."
        self.client.post(self.wallpost_reaction_url, {'reaction': reaction3_text, 'wallpost_id': self.another_wallpost.id})
        another_wallpost_detail_url = "{0}{1}".format(self.project_text_wallpost_url, str(self.another_wallpost.id))
        response = self.client.get(another_wallpost_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data['reactions']), 1)
        self.assertEqual(response.data['reactions'][0]['reaction'], reaction3_text)

        # The first WallPost should still have just two reactions
        response = self.client.get(some_wallpost_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data['reactions']), 2)

        # Delete the first reaction
        response = self.client.delete(reaction1_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)

        # The first WallPost should have only one reaction now
        response = self.client.get(some_wallpost_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data['reactions']), 1)

import json
from random import randint
from datetime import datetime, timedelta

from decimal import Decimal
from bluebottle.bb_projects.models import ProjectPhase
from django.test import TestCase, RequestFactory
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils import timezone
from onepercentclub.tests.utils import OnePercentTestCase

from rest_framework import status

from bluebottle.utils.utils import get_taskmember_model, get_skill_model
from bluebottle.test.factory_models.accounts import BlueBottleUserFactory
from onepercentclub.tests.factory_models.project_factories import OnePercentProjectFactory
from onepercentclub.tests.factory_models.donation_factories import DonationFactory

from ..models import Project


# RequestFactory used for integration tests.
factory = RequestFactory()


class ProjectEndpointTestCase(OnePercentTestCase):
    """
    Integration tests for the Project API.
    """

    def setUp(self):
        """
        Create 26 Project instances.
        """
        self.init_projects()
        self.user = BlueBottleUserFactory.create()

        self.campaign_phase = ProjectPhase.objects.get(slug='campaign')
        self.plan_phase = ProjectPhase.objects.get(slug='done-complete')

        for char in 'abcdefghijklmnopqrstuvwxyz':
            # Put half of the projects in the campaign phase.
            if ord(char) % 2 == 1:
                project = OnePercentProjectFactory.create(title=char * 3, slug=char * 3, status=self.campaign_phase)
            else:
                project = OnePercentProjectFactory.create(title=char * 3, slug=char * 3, status=self.plan_phase)

            project.save()

        self.projects_url = reverse('project_list')


class ProjectApiIntegrationTest(ProjectEndpointTestCase):

    def test_project_list_view(self):
        """
        Tests for Project List view. These basic tests are here because Project is the
        first API to use DRF2. Not all APIs need thorough integration testing like this.
        """

        # Basic test of DRF2.
        response = self.client.get(self.projects_url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['count'], 26)
        self.assertEquals(len(response.data['results']), 10)
        self.assertNotEquals(response.data['next'], None)
        self.assertEquals(response.data['previous'], None)

    def test_project_list_view_query_filters(self):
        """
        Tests for Project List view with filters. These basic tests are here because Project is the
        first API to use DRF2. Not all APIs need thorough integration testing like this.
        """

        # Tests that the phase filter works.
        response = self.client.get('%s?status=%i' % (self.projects_url, self.plan_phase.id))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['count'], 13)
        self.assertEquals(len(response.data['results']), 10)

        # Test that ordering works
        response = self.client.get(self.projects_url + '?ordering=newest')
        self.assertEquals(response.status_code, 200)
        response = self.client.get(self.projects_url + '?ordering=title')
        self.assertEquals(response.status_code, 200)
        response = self.client.get(self.projects_url + '?ordering=deadline')
        self.assertEquals(response.status_code, 200)
        response = self.client.get(self.projects_url + '?ordering=needed')
        self.assertEquals(response.status_code, 200)
        response = self.client.get(self.projects_url + '?ordering=popularity')
        self.assertEquals(response.status_code, 200)

        # Test that combination of arguments works
        response = self.client.get(self.projects_url + '?ordering=deadline&phase=campaign&country=101')
        self.assertEquals(response.status_code, 200)

    def test_project_detail_view(self):
        """ Tests retrieving a project detail from the API. """

        # Get the list of projects.
        response = self.client.get(self.projects_url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Test retrieving the first project detail from the list.
        project = response.data['results'][0]
        response = self.client.get(self.projects_url + str(project['id']))
        self.assertEquals(response.status_code, status.HTTP_200_OK)


class ProjectManageApiIntegrationTest(OnePercentTestCase):
    """
    Integration tests for the Project API.
    """

    def setUp(self):
        self.some_user = BlueBottleUserFactory.create()
        self.another_user = BlueBottleUserFactory.create()

        self.init_projects()

        self.phase_plan_new = ProjectPhase.objects.get(slug='plan-new')
        self.phase_submitted = ProjectPhase.objects.get(slug='plan-submitted')
        self.phase_campaign = ProjectPhase.objects.get(slug='campaign')

        self.manage_projects_url = reverse('project_manage_list')
        self.manage_budget_lines_url = reverse('project-budgetline-list')

    def test_project_create(self):
        """
        Tests for Project Create
        """

        # Check that a new user doesn't have any projects to manage
        self.client.login(username=self.some_user.email, password='testing')
        response = self.client.get(self.manage_projects_url)
        self.assertEquals(response.data['count'], 0)

        # Let's throw a pitch (create a project really)
        response = self.client.post(self.manage_projects_url, {'title': 'This is my smart idea'})
        self.assertEquals(response.data['title'], 'This is my smart idea')

        # Check that it's there, in pitch phase, has got a pitch but no plan yet.
        response = self.client.get(self.manage_projects_url)
        self.assertEquals(response.data['count'], 1)
        self.assertEquals(response.data['results'][0]['status'], self.phase_plan_new.id)
        self.assertEquals(response.data['results'][0]['pitch'], '')

        # Get the project
        project_id = response.data['results'][0]['id']
        response = self.client.get(self.manage_projects_url + str(project_id))
        self.assertEquals(response.status_code, status.HTTP_200_OK, response)
        self.assertEquals(response.data['title'], 'This is my smart idea')

        # Let's check that another user can't get this pitch
        self.client.logout()
        self.client.login(username=self.another_user.email, password='testing')
        response = self.client.get(reverse('project_manage_detail', kwargs={'slug': project_id}))
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN, response)

        # Let's create a pitch for this other user
        response = self.client.post(self.manage_projects_url, {'title': 'My idea is way smarter!'})
        project_url = reverse('project_manage_detail', kwargs={'slug': response.data['slug']})
        self.assertEquals(response.data['title'], 'My idea is way smarter!')

        # Add some values to this project
        project_data = {
            'title': 'My idea is way smarter!',
            'pitch': 'Lorem ipsum, bla bla ',
            'description': 'Some more text'
        }
        response = self.client.put(project_url, json.dumps(project_data), 'application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK, response)

        # Back to the previous pitch. Try to cheat and put it to status approved.
        project_data['status'] = self.phase_campaign.id
        response = self.client.put(project_url, json.dumps(project_data), 'application/json')
        self.assertEquals(response.data['status'], self.phase_plan_new.id, 'status should be reset to previous value')

        # Ok, let's try to submit it. We have to submit all previous data again too.
        project_data['status'] = self.phase_submitted.id
        response = self.client.put(project_url, json.dumps(project_data), 'application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK, response)
        self.assertEquals(response.data['status'], self.phase_submitted.id)

        # Changing the slug for this project should just reset it to the previous value
        project_data['slug'] = 'a-new-slug-should-not-be-possible'
        response_2 = self.client.put(project_url, json.dumps(project_data), 'application/json')
        self.assertEquals(response_2.data['slug'], response.data['slug'], 'changing the slug should not be possible')

        # Set the project to plan phase from the backend
        project = Project.objects.get(slug=response.data.get('slug'))
        project.status = self.phase_campaign
        project_id = project.slug
        project.save()

        # Let's look at the project again. It should be in campaign phase now.
        response = self.client.get(project_url)
        self.assertEquals(response.status_code, status.HTTP_200_OK, response)
        self.assertEquals(response.data['status'], self.phase_campaign.id)

        # Trying to create a project with the same title should result in an error.
        response = self.client.post(self.manage_projects_url, {'title': 'This is my smart idea'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertEquals(response.data['title'][0], 'Project with this Title already exists.')

        # Anonymous user should not be able to find this project through management API.
        self.client.logout()
        response = self.client.get(project_url)
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN, response)

        # Also it should not be visible by the first user.
        self.client.login(username=self.some_user.email, password='testing')
        response = self.client.get(project_url)
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN, response)

    def test_project_budgetlines_crud(self):
        self.client.login(username=self.some_user.email, password='testing')
        project_data = {'title': 'Some project with a goal & budget'}
        response = self.client.post(self.manage_projects_url, project_data)
        self.assertEquals(response.data['title'], project_data['title'])
        project_id = response.data['id']
        project_url = '{0}{1}'.format(self.manage_projects_url, project_id)

        # Check that there aren't any budgetlines
        self.assertEquals(response.data['budget_lines'], [])

        budget = [
            {'project': project_id, 'description': 'Stuff', 'amount': 800},
            {'project': project_id, 'description': 'Things', 'amount': 1200},
            {'project': project_id, 'description': 'Random produce', 'amount': 170}
        ]

        for line in budget:
            response = self.client.post(self.manage_budget_lines_url, line)
            self.assertEquals(response.status_code, status.HTTP_201_CREATED, response)

        # We should have 3 budget lines by now
        response = self.client.get(project_url)
        self.assertEquals(len(response.data['budget_lines']), 3)

        # Let's change a budget_line
        budget_line = response.data['budget_lines'][0]
        budget_line['amount'] = 350
        budget_line_url = "{0}{1}".format(self.manage_budget_lines_url, budget_line['id'])
        response = self.client.put(budget_line_url, json.dumps(budget_line), 'application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK, response)
        self.assertEquals(response.data['amount'], '350.00')

        # Now remove that line
        response = self.client.delete(budget_line_url)
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT, response)
        # Should have 2  budget lines now
        response = self.client.get(project_url)
        self.assertEquals(len(response.data['budget_lines']), 2)

        # Login as another user and try to add a budget line to this project.
        self.client.logout()
        self.client.login(username=self.another_user.email, password='testing')
        new_budget_line = {'project': project_id, 'description': 'I want in too', 'amount': 10000}
        response = self.client.post(self.manage_budget_lines_url, line)
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN, response)


class ProjectWallPostApiIntegrationTest(TestCase):
    """
    Integration tests for the Project Media WallPost API.
    """

    def setUp(self):
        self.some_project = OnePercentProjectFactory.create(slug='someproject')
        self.another_project = OnePercentProjectFactory.create(slug='anotherproject')

        self.some_user = BlueBottleUserFactory.create()
        self.another_user = BlueBottleUserFactory.create()

        self.some_photo = 'apps/projects/test_images/loading.gif'
        self.another_photo = 'apps/projects/test_images/upload.png'

        self.media_wallposts_url = reverse('media_wallpost_list')
        self.media_wallpost_photos_url = reverse('mediawallpost_photo_list')   

        self.text_wallposts_url = reverse('text_wallpost_list')
        self.wallposts_url = reverse('wallpost_list')

    def test_project_media_wallpost_crud(self):
        """
        Tests for creating, retrieving, updating and deleting a Project Media WallPost.
        """
        self.client.login(username=self.some_project.owner.email, password='testing')

        # Create a Project Media WallPost by Project Owner
        # Note: This test will fail when we require at least a video and/or a text but that's what we want.
        wallpost_title = 'This is my super project!'
        response = self.client.post(self.media_wallposts_url, {'title': wallpost_title, 'parent_type': 'project','parent_id': self.some_project.slug})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['title'], wallpost_title)

        # Retrieve the created Project Media WallPost.
        project_wallpost_detail_url = "{0}{1}".format(self.wallposts_url, str(response.data['id']))
        response = self.client.get(project_wallpost_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['title'], wallpost_title)

        # Update the created Project Media WallPost by author.
        new_wallpost_title = 'This is my super-duper project!'
        response = self.client.put(project_wallpost_detail_url, json.dumps({'title': new_wallpost_title, 'parent_type': 'project','parent_id': self.some_project.slug}), 'application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['title'], new_wallpost_title)

        # Delete Project Media WallPost by author
        response = self.client.delete(project_wallpost_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response)

        # Check that creating a WallPost with project slug that doesn't exist reports an error.
        response = self.client.post(self.media_wallposts_url, {'title': wallpost_title, 'parent_type': 'project', 'parent_id': 'allyourbasearebelongtous'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

        # Create Project Media WallPost and retrieve by another user
        response = self.client.post(self.media_wallposts_url, {'title': wallpost_title, 'parent_type': 'project', 'parent_id': self.some_project.slug})
        project_wallpost_detail_url = "{0}{1}".format(self.wallposts_url, str(response.data['id']))
        self.client.logout()
        self.client.login(username=self.some_user.email, password='testing')
        response = self.client.get(project_wallpost_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['title'], wallpost_title)


        # At this moment every one can at media wall-posts.
        # TODO: Decide if/how we want to limit this.

        # Write Project Media WallPost by someone else then Project Owner should fail
        # new_wallpost_title = 'This is not my project...'
        # response = self.client.post(self.media_wallposts_url, {'title': new_wallpost_title, 'parent_type': 'project', 'parent_id': self.some_project.slug})
        # self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

        # Write Project Media WallPost by Project Owner to another Project should fail
        # self.client.logout()
        # self.client.login(username=self.some_project.owner.email, password='testing')
        # new_wallpost_title = 'This is not my project, although I do have a project'
        # response = self.client.post(self.media_wallposts_url, {'title': new_wallpost_title, 'parent_type': 'project', 'parent_id': self.another_project.slug})
        # self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

        # Update Project Media WallPost by someone else than Project Owner should fail
        second_wallpost_title = "My project rocks!"
        response = self.client.post(self.media_wallposts_url, {'title': second_wallpost_title, 'parent_type': 'project', 'parent_id': self.some_project.slug})
        self.client.logout()
        self.client.login(username=self.some_user.email, password='testing')
        response = self.client.put(project_wallpost_detail_url, {'title': new_wallpost_title, 'parent_type': 'project', 'parent_id': self.some_project.slug})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

        # Deleting a Project Media WallPost by non-author user should fail.
        response = self.client.delete(project_wallpost_detail_url)  # some_user is still logged in.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response)

        # Retrieve a list of the two Project Media WallPosts that we've just added should work
        response = self.client.get(self.wallposts_url,  {'parent_type': 'project', 'parent_id': self.some_project.slug})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['title'], second_wallpost_title)
        self.assertEqual(response.data['results'][1]['title'], wallpost_title)
        self.client.logout()

    def test_project_media_wallpost_photo(self):
        """
        Test connecting photos to wallposts
        """
        self.client.login(username=self.some_project.owner.email, password='testing')

        # Typically the photos are uploaded before the wallpost is uploaded so we simulate that here
        photo_file = open(self.some_photo, mode='rb')
        response = self.client.post(self.media_wallpost_photos_url, {'photo': photo_file})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        some_photo_detail_url = "{0}{1}".format(self.media_wallpost_photos_url, response.data['id'])

        # Create a Project Media WallPost by Project Owner
        wallpost_title = 'Here are some pics!'
        response = self.client.post(self.media_wallposts_url, {'title': wallpost_title, 'parent_type': 'project', 'parent_id': self.some_project.slug})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['title'], wallpost_title)
        some_wallpost_id = response.data['id']
        some_wallpost_detail_url = "{0}{1}".format(self.wallposts_url, some_wallpost_id)

        # Try to connect the photo to this new wallpost
        response = self.client.put(some_photo_detail_url, json.dumps({'mediawallpost': some_wallpost_id}), 'application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        # check that the wallpost now has 1 photo
        response = self.client.get(some_wallpost_detail_url)
        self.assertEqual(len(response.data['photos']), 1)

        # Let's upload another photo
        photo_file = open(self.another_photo, mode='rb')
        response = self.client.post(self.media_wallpost_photos_url, {'photo': photo_file})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        another_photo_detail_url = "{0}{1}".format(self.media_wallpost_photos_url, response.data['id'])

        # Create a wallpost by another user
        self.client.logout()
        self.client.login(username=self.another_project.owner.email, password='testing')
        wallpost_title = 'Muy project is waaaaaay better!'
        response = self.client.post(self.media_wallposts_url, {'title': wallpost_title, 'parent_type': 'project', 'parent_id': self.another_project.slug})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['title'], wallpost_title)
        another_wallpost_id = response.data['id']
        antoher_wallpost_detail_url = "{0}{1}".format(self.media_wallposts_url, another_wallpost_id)

        # The other shouldn't be able to use the photo of the first user
        response = self.client.put(another_photo_detail_url, {'mediawallpost': another_wallpost_id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)
        response = self.client.put(another_photo_detail_url, {'mediawallpost': some_wallpost_id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

        # Make sure the first user can't connect it's picture to someone else's wallpost
        self.client.logout()
        self.client.login(username=self.some_project.owner.email, password='testing')
        response = self.client.put(another_photo_detail_url, json.dumps({'mediawallpost': another_wallpost_id}), 'application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

        #  Create a text wallpost. Adding a photo to that should be denied.
        text = "You have something nice going on here."
        response = self.client.post(self.text_wallposts_url, {'text': text, 'parent_type': 'project', 'parent_id': self.another_project.slug})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        text_wallpost_id = response.data['id']
        response = self.client.put(another_photo_detail_url, json.dumps({'mediawallpost': another_wallpost_id}), 'application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

        # Add that second photo to our first wallpost and verify that will now contain two photos.
        response = self.client.put(another_photo_detail_url, json.dumps({'mediawallpost': some_wallpost_id}), 'application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        response = self.client.get(some_wallpost_detail_url)
        self.assertEqual(len(response.data['photos']), 2)

    def test_project_text_wallpost_crud(self):
        """
        Tests for creating, retrieving, updating and deleting text wallposts.
        """

        # Create text wallpost as not logged in guest should be denied
        text1 = 'Great job!'
        response = self.client.post(self.text_wallposts_url, {'text': text1, 'parent_type': 'project', 'parent_id': self.some_project.slug})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.login(username=self.some_user.email, password='testing')

        # Create TextWallPost as a logged in member should be allowed
        response = self.client.post(self.text_wallposts_url, {'text': text1, 'parent_type': 'project', 'parent_id': self.some_project.slug})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(text1 in response.data['text'])

        # Retrieve text wallpost through WallPosts api
        wallpost_detail_url = "{0}{1}".format(self.wallposts_url, str(response.data['id']))
        response = self.client.get(wallpost_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTrue(text1 in response.data['text'])

        # Retrieve text wallpost through TextWallPosts api
        wallpost_detail_url = "{0}{1}".format(self.wallposts_url, str(response.data['id']))
        response = self.client.get(wallpost_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTrue(text1 in response.data['text'])

        self.client.logout()
        self.client.login(username=self.another_user.email, password='testing')

        # Retrieve text wallpost through projectwallposts api by another user
        wallpost_detail_url = "{0}{1}".format(self.wallposts_url, str(response.data['id']))
        response = self.client.get(wallpost_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTrue(text1 in response.data['text'])

        # Create TextWallPost without a text should return an error
        response = self.client.post(self.text_wallposts_url, {'text': '', 'parent_type': 'project', 'parent_id': self.some_project.slug})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertIsNotNone(response.data['text'])

        text2 = "I liek this project!"

        # Create TextWallPost as another logged in member should be allowed
        response = self.client.post(self.text_wallposts_url, {'text': text2, 'parent_type': 'project', 'parent_id': self.some_project.slug})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(text2 in response.data['text'])

        # Update TextWallPost by author is allowed
        text2a = 'I like this project!'
        wallpost_detail_url = "{0}{1}".format(self.wallposts_url, str(response.data['id']))
        response = self.client.put(wallpost_detail_url, json.dumps( {'text': text2a, 'parent_type': 'project', 'parent_id': self.some_project.slug}), 'application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTrue(text2a in response.data['text'])

        self.client.logout()
        self.client.login(username=self.some_user.email, password='testing')

        # Update TextWallPost by another user (not the author) is not allowed
        text2b = 'Mess this up!'
        wallpost_detail_url = "{0}{1}".format(self.wallposts_url, str(response.data['id']))
        response = self.client.put(wallpost_detail_url, {'text': text2b, 'project': self.some_project.slug})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_projectwallpost_list(self):
        """
        Tests for list and (soft)deleting wallposts
        """

        # Create a bunch of Project Text WallPosts
        self.client.login(username=self.some_user.email, password='testing')
        for char in 'abcdefghijklmnopqrstuv':
            text = char * 15
            self.client.post(self.text_wallposts_url, {'text': text, 'parent_type': 'project', 'parent_id': self.some_project.slug})

        self.client.logout()

        # And a bunch of Project Media WallPosts
        self.client.login(username=self.some_project.owner.email, password='testing')
        for char in 'wxyz':
            title = char * 15
            self.client.post(self.media_wallposts_url, {'title': title, 'parent_type': 'project', 'parent_id': self.some_project.slug})

        # Retrieve a list of the 26 Project WallPosts
        # View Project WallPost list works for author
        response = self.client.get(self.wallposts_url,  {'parent_type': 'project', 'parent_id': self.some_project.slug})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
        self.assertEqual(response.data['count'], 26)
        mediawallpost = response.data['results'][0]

        # Check that we're correctly getting a list with mixed types.
        self.assertEqual(mediawallpost['type'], 'media')

        # Delete a Media WallPost and check that we can't retrieve it anymore
        project_wallpost_detail_url = "{0}{1}".format(self.wallposts_url, mediawallpost['id'])
        response = self.client.delete(project_wallpost_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(project_wallpost_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

        # WallPost List count should have decreased after deleting one
        response = self.client.get(self.wallposts_url,  {'parent_type': 'project', 'parent_id': self.some_project.slug})
        self.assertEqual(response.data['count'], 25)

        # View Project WallPost list works for guests.
        self.client.logout()
        response = self.client.get(self.wallposts_url,  {'parent_type': 'project', 'parent_id': self.some_project.slug})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data['results']), 5)
        self.assertEqual(response.data['count'], 25)

        # Test filtering wallposts by different projects works.
        self.client.login(username=self.another_project.owner.email, password='testing')
        for char in 'ABCD':
            title = char * 15
            self.client.post(self.media_wallposts_url, {'title': title, 'parent_type': 'project', 'parent_id': self.another_project.slug})
        response = self.client.get(self.wallposts_url,  {'parent_type': 'project', 'parent_id': self.some_project.slug})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['count'], 25)
        response = self.client.get(self.wallposts_url,  {'parent_type': 'project', 'parent_id': self.another_project.slug})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['count'], 4)


class ChangeProjectStatuses(ProjectEndpointTestCase):

    def set_date_submitted(self, project):
        #Set a date_submitted value for the project
        yesterday = datetime.now() - timedelta(days=1)
        project.date_submitted = yesterday
        project.save()
        self.assertEquals(project.date_submitted, yesterday)

    def test_change_status_to_submitted(self):
        """
        Changing project status to submitted sets the date_submitted field
        """
        project = Project.objects.get(id=randint(1, Project.objects.count()))
        self.assertTrue(project.date_submitted is None)

        #Change status of project to Needs work
        project.status = ProjectPhase.objects.get(slug="plan-submitted")
        project.save()

        self.assertTrue(project.date_submitted is not None)

    def test_change_status_to_campaign(self):
        """
        Changing project status to campaign sets the campaign_started field
        """
        project = Project.objects.get(id=randint(1, Project.objects.count()))
        self.assertTrue(project.date_submitted is not None)
        self.assertTrue(project.campaign_started is None)

        #Change status of project to Needs work
        project.status = ProjectPhase.objects.get(slug="campaign")
        project.save()

        self.assertTrue(project.date_submitted is not None)
        self.assertTrue(project.campaign_started is not None)

    def test_change_status_to_need_to_work(self):
        """
        Changing status to needs work clears the date_submitted field of a project
        """
        project = Project.objects.get(id=randint(1, Project.objects.count()))
        self.set_date_submitted(project)

        #Change status of project to Needs work
        project.status = ProjectPhase.objects.get(slug="plan-needs-work")
        project.save()

        self.assertEquals(project.date_submitted, None)

    def test_change_status_to_new(self):
        """
        Changing status to new clears the date_submitted field of a project
        """
        project = Project.objects.get(id=randint(1, Project.objects.count()))
        self.set_date_submitted(project)

        #Change status of project to Needs work
        project.status = ProjectPhase.objects.get(slug="plan-new")
        project.save()

        self.assertEquals(project.date_submitted, None)

    def test_campaign_project_got_funded_no_overfunding(self):
        """
        A project gets a donation and gets funded. The project does not allow overfunding so the status changes,
        the campaign funded field is populated and campaign_ended field is populated
        """
        project = OnePercentProjectFactory.create(title="testproject", slug="testproject",
                                                  status=ProjectPhase.objects.get(slug="campaign"),
                                                  amount_asked=100, allow_overfunding=False)

        self.assertTrue(project.campaign_ended is None)
        self.assertTrue(project.campaign_funded is None)

        donation = DonationFactory.create(user=self.user, project=project, amount=10000)

        self.assertTrue(project.campaign_ended is not None)
        self.assertTrue(project.campaign_funded is not None)
        self.assertEquals(project.status, ProjectPhase.objects.get(slug="done-complete"))

    def test_campaign_project_got_funded_allow_overfunding(self):
        """
        A project gets funded and allows overfunding. The project status does not change, the campaign_funded field
        is populated but the campaign_ended field is not populated
        """
        project = OnePercentProjectFactory.create(title="testproject", slug="testproject",
                                                  status=ProjectPhase.objects.get(slug="campaign"),
                                                  amount_asked=100)

        self.assertTrue(project.campaign_ended is None)
        self.assertTrue(project.campaign_funded is None)

        donation = DonationFactory.create(user=self.user, project=project, amount=10000)

        self.assertTrue(project.campaign_ended is None)
        self.assertTrue(project.campaign_funded is not None)
        self.assertEquals(project.status, ProjectPhase.objects.get(slug="campaign"))

    def test_campaign_project_not_funded(self):
        """
        A donation is made but the project is not funded. The status doesn't change and neither the campaign_ended
        or campaign_funded are populated.
        """
        project = OnePercentProjectFactory.create(title="testproject", slug="testproject",
                                                  status=ProjectPhase.objects.get(slug="campaign"),
                                                  amount_asked=100)

        self.assertTrue(project.campaign_ended is None)
        self.assertTrue(project.campaign_funded is None)

        donation = DonationFactory.create(user=self.user, project=project, amount=99)

        self.assertTrue(project.campaign_ended is None)
        self.assertTrue(project.campaign_funded is None)
        self.assertEquals(project.status, ProjectPhase.objects.get(slug="campaign"))

    def test_project_expired(self):
        """
        The deadline of a project expires but its not funded. The status changes, the campaign_ended field is populated
        with the deadline, the campaign_funded field is empty.
        """
        project = OnePercentProjectFactory.create(title="testproject", slug="testproject",
                                                  status=ProjectPhase.objects.get(slug="campaign"),
                                                  amount_asked=100)

        self.assertTrue(project.campaign_ended is None)
        self.assertTrue(project.campaign_funded is None)

        project.deadline = timezone.now() - timedelta(days=10)
        project.save()

        self.assertEquals(project.campaign_ended, project.deadline)
        self.assertTrue(project.campaign_funded is None)
        self.assertEquals(project.status, ProjectPhase.objects.get(slug="done-incomplete"))

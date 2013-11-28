import json
from decimal import Decimal

from django.test import TestCase, RequestFactory
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from bluebottle.bluebottle_utils.tests import UserTestsMixin, generate_random_slug

from apps.organizations.tests import OrganizationTestsMixin
from apps.wallposts.models import TextWallPost
from apps.fund.models import DonationStatuses, Donation, Order
from apps.projects.models import ProjectPlan, ProjectCampaign

from ..models import Project, ProjectPhases, ProjectPitch


class ProjectTestsMixin(OrganizationTestsMixin, UserTestsMixin):
    """ Mixin base class for tests using projects. """

    def create_project(self, organization=None, owner=None, title=None, phase='pitch', slug=None, money_asked=0):
        """
        Create a 'default' project with some standard values so it can be
        saved to the database, but allow for overriding.

        The returned object is saved to the database.
        """
        if not owner:
            # Create a new user with a random username
            owner = self.create_user()

        if not slug:
            slug = generate_random_slug()
            while Project.objects.filter(slug=slug).exists():
                slug = generate_random_slug()

        if not title:
            title = generate_random_slug()
            while Project.objects.filter(title=title).exists():
                title = generate_random_slug()

        project = Project(owner=owner, title=title, slug=slug, phase=phase)
        project.save()

        project.projectpitch.title = title
        project.projectpitch.status = ProjectPitch.PitchStatuses.new
        project.projectpitch.save()

        if money_asked:

            project.projectplan = ProjectPlan(title=project.title, project=project)
            project.projectplan.status = 'approved'

            # add an organization so we can create pay-outs
            project.projectplan.organization = self.create_organization()
            project.projectplan.save()

            project.projectcampaign = ProjectCampaign(status='running', project=project, money_asked=money_asked)
            project.projectcampaign.save()
            project.projectcampaign.update_money_donated()

            project.phase = ProjectPhases.campaign
            project.save()

        return project


class ProjectWallPostTestsMixin(ProjectTestsMixin):
    """ Mixin base class for tests using wallposts. """

    def create_project_text_wallpost(self, text='Some smart comment.', project=None, author=None):
        if not project:
            project = self.create_project()
        if not author:
            author = self.create_user()
        content_type = ContentType.objects.get_for_model(Project)
        wallpost = TextWallPost(content_type=content_type, object_id=project.id, author=author)
        wallpost.text = text
        wallpost.save()
        return wallpost

# RequestFactory used for integration tests.
factory = RequestFactory()


class ProjectApiIntegrationTest(ProjectTestsMixin, TestCase):
    """
    Integration tests for the Project API.
    """

    def setUp(self):
        """
        Create 26 Project instances.
        """
        for char in 'abcdefghijklmnopqrstuvwxyz':
            project = self.create_project(title=char * 3, slug=char * 3)
            if ord(char) % 2 == 1:
                # Put half of the projects in the campaign phase.
                project.projectplan = ProjectPlan(title=project.title)
                project.projectplan.status = 'approved'
                project.projectplan.save()
                project.phase = ProjectPhases.campaign
                project.save()
            else:
                project.projectplan = ProjectPlan(title=project.title)
                project.projectplan.save()
                project.phase = ProjectPhases.plan
                project.save()

        self.projects_url = '/api/projects/projects/'

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
        response = self.client.get(self.projects_url + '?phase=plan')
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


class ProjectManageApiIntegrationTest(ProjectTestsMixin, TestCase):
    """
    Integration tests for the Project API.
    """

    def setUp(self):
        self.some_user = self.create_user()
        self.another_user = self.create_user()

        self.manage_projects_url = '/api/projects/manage/'
        self.manage_pitches_url = '/api/projects/pitches/manage/'

    def test_pitch_create(self):
        """
        Tests for Project Pitch Create
        """

        # Check that a new user doesn't have any projects to manage
        self.client.login(username=self.some_user.email, password='password')
        response = self.client.get(self.manage_projects_url)
        self.assertEquals(response.data['count'], 0)

        # Let's throw a pitch (create a project really)
        response = self.client.post(self.manage_projects_url, {'title': 'This is my smart idea'})
        self.assertEquals(response.data['title'], 'This is my smart idea')

        # Check that it's there, in pitch phase, has got a pitch but no plan yet.
        response = self.client.get(self.manage_projects_url)
        self.assertEquals(response.data['count'], 1)
        self.assertEquals(response.data['results'][0]['phase'], ProjectPhases.pitch)
        self.assertEquals(response.data['results'][0]['plan'], None)

        # Get the pitch
        pitch_id = response.data['results'][0]['pitch']
        response = self.client.get(self.manage_pitches_url + str(pitch_id))
        self.assertEquals(response.status_code, status.HTTP_200_OK, response)
        self.assertEquals(response.data['title'], 'This is my smart idea')

        # Let's check that another user can't get this pitch
        self.client.logout()
        self.client.login(username=self.another_user.email, password='password')
        response = self.client.get(self.manage_pitches_url + str(pitch_id))
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN, response)

        # Let's create a pitch for this other user
        response = self.client.post(self.manage_projects_url, {'title': 'My idea is way smarter!'})
        project_slug = response.data['id']
        project_url = self.manage_projects_url + project_slug
        self.assertEquals(response.data['title'], 'My idea is way smarter!')
        pitch_id = response.data['pitch']
        pitch_url = self.manage_pitches_url + str(pitch_id)

        # Add some values to this pitch
        pitch_data = {'title': 'My idea is quite smart!', 'latitude': '52.987245', 'longitude': '-5.8754',
                      'pitch': 'Lorem ipsum, bla bla ', 'description': 'Some more text'}
        response = self.client.put(pitch_url, json.dumps(pitch_data), 'application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK, response)

        # Let's try to be smart and create another pitch. This should fail. You can have only have one running project.
        response = self.client.post(self.manage_projects_url, {'title': 'I am such a smart ass...'})
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN, response)

        # Back to the previous pitch. Try to cheat and put it to status approved.
        pitch_data['status'] = 'approved'
        response = self.client.put(pitch_url, json.dumps(pitch_data), 'application/json')
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST, response)
        
        # Ok, let's try to submit it. We have to submit all previous data again too.
        pitch_data['status'] = 'submitted'
        response = self.client.put(pitch_url, json.dumps(pitch_data), 'application/json')
        self.assertEquals(response.status_code, status.HTTP_200_OK, response)
        self.assertEquals(response.data['status'], 'submitted')

        # Changing this pitch specs for this project should fail now.
        pitch_data['title'] = 'Changed title'
        response = self.client.put(pitch_url, json.dumps(pitch_data), 'application/json')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN, response)

        # Set the project to plan phase from the backend
        project = Project.objects.get(slug=project_slug)
        project.phase = ProjectPhases.plan
        project.save()

        # Let's look at the project again. It should have a project plan and be in plan phase.
        response = self.client.get(project_url)
        self.assertEquals(response.status_code, status.HTTP_200_OK, response)
        self.assertEquals(response.data['phase'], ProjectPhases.plan)
        plan_id = response.data['plan']
        self.assertIsNotNone(plan_id)


class ProjectWallPostApiIntegrationTest(ProjectTestsMixin, UserTestsMixin, TestCase):
    """
    Integration tests for the Project Media WallPost API.
    """

    def setUp(self):
        self.some_project = self.create_project(slug='someproject')
        self.another_project = self.create_project(slug='anotherproject')

        self.some_user = self.create_user()
        self.another_user = self.create_user()

        self.some_photo = 'apps/projects/test_images/loading.gif'
        self.another_photo = 'apps/projects/test_images/upload.png'

        self.media_wallposts_url = '/api/wallposts/mediawallposts/'
        self.media_wallpost_photos_url = '/api/wallposts/photos/'

        self.text_wallposts_url = '/api/wallposts/textwallposts/'
        self.wallposts_url = '/api/wallposts/'

    def test_project_media_wallpost_crud(self):
        """
        Tests for creating, retrieving, updating and deleting a Project Media WallPost.
        """
        self.client.login(username=self.some_project.owner.email, password='password')

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
        self.client.login(username=self.some_user.email, password='password')
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
        # self.client.login(username=self.some_project.owner.email, password='password')
        # new_wallpost_title = 'This is not my project, although I do have a project'
        # response = self.client.post(self.media_wallposts_url, {'title': new_wallpost_title, 'parent_type': 'project', 'parent_id': self.another_project.slug})
        # self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

        # Update Project Media WallPost by someone else than Project Owner should fail
        second_wallpost_title = "My project rocks!"
        response = self.client.post(self.media_wallposts_url, {'title': second_wallpost_title, 'parent_type': 'project', 'parent_id': self.some_project.slug})
        self.client.logout()
        self.client.login(username=self.some_user.email, password='password')
        response = self.client.put(project_wallpost_detail_url, {'title': new_wallpost_title, 'parent_type': 'project', 'parent_id': self.some_project.slug})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

        # Deleting a Project Media WallPost by non-author user should fail.
        response = self.client.delete(project_wallpost_detail_url)  # some_user is still logged in.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response)

        # Retrieve a list of the two Project Media WallPosts that we've just added should work
        response = self.client.get(self.wallposts_url,  {'project': self.some_project.slug})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['title'], second_wallpost_title)
        self.assertEqual(response.data['results'][1]['title'], wallpost_title)
        self.client.logout()

    def test_project_media_wallpost_photo(self):
        """
        Test connecting photos to wallposts
        """
        self.client.login(username=self.some_project.owner.email, password='password')

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
        self.client.login(username=self.another_project.owner.email, password='password')
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
        self.client.login(username=self.some_project.owner.email, password='password')
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

        self.client.login(username=self.some_user.email, password='password')

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
        self.client.login(username=self.another_user.email, password='password')

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
        self.client.login(username=self.some_user.email, password='password')

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
        self.client.login(username=self.some_user.email, password='password')
        for char in 'abcdefghijklmnopqrstuv':
            text = char * 15
            self.client.post(self.text_wallposts_url, {'text': text, 'parent_type': 'project', 'parent_id': self.some_project.slug})

        self.client.logout()

        # And a bunch of Project Media WallPosts
        self.client.login(username=self.some_project.owner.email, password='password')
        for char in 'wxyz':
            title = char * 15
            self.client.post(self.media_wallposts_url, {'title': title, 'parent_type': 'project', 'parent_id': self.some_project.slug})

        # Retrieve a list of the 26 Project WallPosts
        # View Project WallPost list works for author
        response = self.client.get(self.wallposts_url,  {'project': self.some_project.slug})
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
        response = self.client.get(self.wallposts_url,  {'project': self.some_project.slug})
        self.assertEqual(response.data['count'], 25)

        # View Project WallPost list works for guests.
        self.client.logout()
        response = self.client.get(self.wallposts_url,  {'project': self.some_project.slug})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data['results']), 5)
        self.assertEqual(response.data['count'], 25)

        # Test filtering wallposts by different projects works.
        self.client.login(username=self.another_project.owner.email, password='password')
        for char in 'ABCD':
            title = char * 15
            self.client.post(self.media_wallposts_url, {'title': title, 'parent_type': 'project', 'parent_id': self.another_project.slug})
        response = self.client.get(self.wallposts_url,  {'parent_type': 'project', 'parent_id': self.some_project.slug})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['count'], 25)
        response = self.client.get(self.wallposts_url,  {'parent_type': 'project', 'parent_id': self.another_project.slug})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['count'], 4)


class CalculateProjectMoneyDonatedTest(ProjectTestsMixin, TestCase):

    def setUp(self):
        self.some_project = self.create_project(money_asked=500000)
        self.another_project = self.create_project(money_asked=500000)

        self.some_user = self.create_user()
        self.another_user = self.create_user()

    def test_nr_days_remaining(self):
        import datetime
        today = datetime.datetime.now()
        self.assertEqual(self.some_project.projectcampaign.nr_days_remaining, 0)
        self.some_project.projectcampaign.deadline = today + datetime.timedelta(days=15)
        self.assertEqual(self.some_project.projectcampaign.nr_days_remaining, 15)

    def test_percentage_funded(self):
        """ Check that the percentages are calculated correctly """
        self.assertEqual(self.some_project.projectcampaign.percentage_funded, 0.0)
        campaign = self.some_project.projectcampaign
        campaign.money_donated = 10000
        self.assertEqual(campaign.percentage_funded, 2.0)
        campaign.money_donated = 500000
        self.assertEqual(campaign.percentage_funded, 100.0)
        campaign.money_donated = 1000000
        self.assertEqual(campaign.percentage_funded, 100.0)

    def test_donated_amount(self):
        # Some project have money_asked of 5000000 (cents that is)
        self.assertEqual(self.some_project.projectcampaign.money_asked, 500000)

        # A project without donations should have money_donated of 0
        self.assertEqual(self.some_project.projectcampaign.money_donated, 0)

        # Create a new donation of 15 in status 'new'. project money donated should be 0
        first_donation = self._create_donation(user=self.some_user, project=self.some_project, amount=1500,
                                               status=DonationStatuses.new)
        self.assertEqual(self.some_project.projectcampaign.money_donated, 0)
        

        # Create a new donation of 25 in status 'in_progress'. project money donated should be 0.
        second_donation = self._create_donation(user=self.some_user, project=self.some_project, amount=2500,
                                                status=DonationStatuses.in_progress)
        self.assertEqual(self.some_project.projectcampaign.money_donated, 0)

        # Setting the first donation to status 'paid' money donated should be 1500
        first_donation.status = DonationStatuses.paid
        first_donation.save()
        self.assertEqual(self.some_project.projectcampaign.money_donated, 1500)

        # Setting the second donation to status 'pending' money donated should be 40
        second_donation.status = DonationStatuses.pending
        second_donation.save()
        self.assertEqual(self.some_project.projectcampaign.money_donated, 4000)

    def _create_donation(self, user=None, amount=None, project=None, status=DonationStatuses.new):
        """ Helper method for creating donations."""
        if not project:
            project = self.create_project()
            project.save()

        if not user:
            user = self.create_user()

        if not amount:
            amount = Decimal('10.00')

        order = Order.objects.create()
        donation = Donation.objects.create(user=user, amount=amount, status=status, project=project, order=order)

        return donation


class ProjectPhaseLoggerTest(ProjectTestsMixin, TestCase):
    def setUp(self):
        self.some_project = self.create_project()

    def test_phase_change_logged(self):
        # One phase should be logged due to creation of the project
        self.assertEqual(1, self.some_project.projectphaselog_set.count())
        
        # change the phase, it should be logged
        self.some_project.phase = ProjectPhases.plan
        self.some_project.save()

        self.assertEqual(2, self.some_project.projectphaselog_set.count())


class FailedProjectTest(ProjectTestsMixin, TestCase):
    """ Verify that the project is marked as failed when pitch/plan is rejected """
    def setUp(self):
        self.some_project = self.create_project(phase='plan')

    def test_pitch_rejected(self):
        self.some_project.projectpitch.status = ProjectPitch.PitchStatuses.rejected
        self.some_project.projectpitch.save()
        self.assertEqual(self.some_project.phase, ProjectPhases.failed)


    def test_plan_rejected(self):
        self.some_project.projectplan.status = ProjectPlan.PlanStatuses.rejected
        self.some_project.projectplan.save()

        self.assertEqual(self.some_project.phase, ProjectPhases.failed)

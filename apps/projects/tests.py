from decimal import Decimal
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.test import TestCase, RequestFactory
from django.utils import timezone
from rest_framework import status
from apps.bluebottle_utils.tests import UserTestsMixin, generate_random_slug
from apps.organizations.tests import OrganizationTestsMixin
from apps.media.tests import MediaTestsMixin
from .views import ProjectList, ProjectDetail
from .models import Project, IdeaPhase, FundPhase, ActPhase, ResultsPhase, AbstractPhase


class ProjectTestsMixin(OrganizationTestsMixin, UserTestsMixin):
    """ Mixin base class for tests using projects. """

    def create_project(self, organization=None, owner=None, title='',
                       slug='', latitude=None, longitude=None):
        """
        Create a 'default' project with some standard values so it can be
        saved to the database, but allow for overriding.

        The returned object is saved to the database.
        """

        if not latitude:
            latitude = Decimal('-11.2352')

        if not longitude:
            longitude = Decimal('-84.123')

        if not organization:
            organization = self.create_organization()
            organization.save()

        if not owner:
            # Create a new user with a random username
            owner = self.create_user()
        owner.save()

        if not slug:
            slug = generate_random_slug()
            while Project.objects.filter(slug=slug).exists():
                 slug = generate_random_slug()

        project = Project(
            organization=organization, owner=owner, title=title, slug=slug,
            latitude=latitude, longitude=longitude
        )

        project.save()

        return project


class FundPhaseTestMixin(object):
    def create_fundphase(self, project, budget_total=15000, money_asked=5000):
        """ Create (but not save) a fund phase. """
        fundphase = FundPhase()
        fundphase.project = project
        fundphase.budget_total = budget_total
        fundphase.money_asked = money_asked
        fundphase.startdate = timezone.now().date()
        fundphase.save()
        return fundphase


class ProjectTests(TestCase, ProjectTestsMixin, FundPhaseTestMixin,
                   MediaTestsMixin):
    """ Tests for projects. """

    def setUp(self):
        """ Every test in this suite requires a project. """
        self.project = self.create_project(title='Banana Project', slug='banana')

    def test_amounts(self):
        """ Test calculation of donation amounts """

        phase = self.create_fundphase(self.project, 12000, 3520)
        self.assertEquals(self.project.money_asked, 3520)

        self.project.fundphase.money_donated = 2155
        self.assertEquals(self.project.money_donated, 2155)

    def test_money_donated_default(self):
        """
        Tests for the default value of money_donated.
        """

        # Saving a new phase should have money_donated set to 0.
        phase = self.create_fundphase(self.project)
        self.assertEquals(phase.money_donated, 0)

        # Saving the phase again with money_donated set shouldn't it back to 0.
        phase.money_donated = 10
        phase.save()
        self.assertNotEqual(phase.money_donated, 0)

        # Saving a phase with money_donated set before save() shouldn't set it to 0.
        funProject = self.create_project(title='Fun Project')
        phase = self.create_fundphase(funProject)
        phase.money_donated = 20
        phase.save()
        self.assertNotEqual(phase.money_donated, 0)

    def test_phase_dates_sync(self):
        """
        Tests that the auto-sync phase start / end date code works.
        """
        today = timezone.now().date()
        two_days_timedelta = timedelta(days=2)
        one_week_timedelta = timedelta(weeks=1)

        # Basic test for the auto-setting previous enddate.
        ideaphase = IdeaPhase(project=self.project)
        ideaphase.startdate = today
        ideaphase.save()
        fundphase = self.create_fundphase(self.project)

        # Refresh the data and test:
        ideaphase = IdeaPhase.objects.get(id=ideaphase.id)
        self.assertTrue(fundphase.startdate == ideaphase.enddate)


        # Tests that previous phase start date is adjusted when the previous
        # phase end date is eariler than the previous phase start date.
        fundphase.startdate = today - two_days_timedelta
        fundphase.save()

        # Refresh the data and test:
        ideaphase = IdeaPhase.objects.get(id=ideaphase.id)
        self.assertTrue(fundphase.startdate == ideaphase.enddate)


        # Test for the auto-setting next startdate.
        resultsphase = ResultsPhase(project=self.project)
        resultsphase.startdate = today + two_days_timedelta
        resultsphase.save()
        actphase = ActPhase(project=self.project)
        actphase.startdate = today
        actphase.enddate = today + one_week_timedelta
        actphase.save()

        # Refresh the data and test:
        resultsphase = ResultsPhase.objects.get(id=resultsphase.id)
        self.assertTrue(resultsphase.startdate == actphase.enddate)

        # Tests that next phase end date is adjusted when the next phase start
        # date is later than the next phase end date.
        actphase = ActPhase.objects.get(id=actphase.id)
        fundphase = FundPhase.objects.get(id=fundphase.id)

        # The current state of things:
        self.assertEquals(fundphase.startdate, today - two_days_timedelta)
        self.assertEquals(fundphase.enddate, today)
        self.assertEquals(actphase.startdate, fundphase.enddate) # today
        self.assertEquals(actphase.enddate, today + one_week_timedelta)

        # Change the fund phase end date to be later than act phase end date.
        fundphase.enddate = today + timedelta(weeks=2)
        fundphase.save()

        # Refresh the data and test:
        actphase = ActPhase.objects.get(id=actphase.id)
        self.assertEquals(fundphase.enddate, actphase.startdate)
        # This is the important test.
        self.assertEquals(actphase.enddate, actphase.startdate)


        # Final refresh and tests:
        ideaphase = IdeaPhase.objects.get(id=ideaphase.id)
        fundphase = FundPhase.objects.get(id=fundphase.id)
        actphase = ActPhase.objects.get(id=actphase.id)
        resultsphase = ResultsPhase.objects.get(id=resultsphase.id)
        self.assertTrue(ideaphase.enddate == fundphase.startdate)
        self.assertTrue(fundphase.enddate == actphase.startdate)
        self.assertTrue(actphase.enddate == resultsphase.startdate)

    def test_phase_validation(self):
        """
        Tests that the phase validation is working.
        """

        # Setup sample phase.
        phase = self.create_fundphase(self.project)
        phase.startdate = timezone.now().date()
        phase.status = AbstractPhase.PhaseStatuses.progress
        phase.save()

        # Check that the validation error is raised.
        phase.enddate =  timezone.now().date() - timedelta(weeks=2)
        self.assertRaises(ValidationError, phase.full_clean)

        # Set a correct value and confirm there's no problem.
        phase.enddate =  timezone.now().date() + timedelta(weeks=2)
        phase.full_clean()
        phase.save()


# RequestFactory used for integration tests.
factory = RequestFactory()


class ProjectApiIntegrationTest(FundPhaseTestMixin, ProjectTestsMixin, TestCase):
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
                # Put half of the projects are in the fund phase.
                fundphase = self.create_fundphase(project)
                project.phase = Project.ProjectPhases.fund
                project.save()

        self.list_view = ProjectList.as_view()
        self.list_view_count = 10
        self.detail_view = ProjectDetail.as_view()
        self.api_base = '/i18n/api/projects/'

    def test_drf2_list_view(self):
        """
        Tests for Project Root view. These basic tests are here because Project
        is the first API to use DRF2 and DRF2 hasn't been released yet. Not all
        DRF views need thorough integration testing like this.
        """

        # Basic test of DRF2.
        request = factory.get(self.api_base)
        response = self.list_view(request).render()
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['count'], 26)
        self.assertEquals(len(response.data['results']), self.list_view_count)
        self.assertNotEquals(response.data['next'], None)
        self.assertEquals(response.data['previous'], None)

        # Tests that the next link works.
        request = factory.get(response.data['next'])
        response = self.list_view(request).render()
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['count'], 26)
        self.assertEquals(len(response.data['results']), self.list_view_count)
        self.assertNotEquals(response.data['next'], None)
        self.assertNotEquals(response.data['previous'], None)

        # Tests that the previous link works.
        request = factory.get(response.data['previous'])
        response = self.list_view(request).render()
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['count'], 26)
        self.assertEquals(len(response.data['results']), self.list_view_count)
        self.assertNotEquals(response.data['next'], None)
        self.assertEquals(response.data['previous'], None)

        # Tests that the last page works.
        request = factory.get(self.api_base + '?page=3')
        response = self.list_view(request).render()
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['count'], 26)
        self.assertEquals(len(response.data['results']), 26 % self.list_view_count)
        self.assertEquals(response.data['next'], None)
        self.assertNotEquals(response.data['previous'], None)

        # Tests that the previous link from the last page works.
        request = factory.get(response.data['previous'])
        response = self.list_view(request).render()
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['count'], 26)
        self.assertEquals(len(response.data['results']), self.list_view_count)
        self.assertNotEquals(response.data['next'], None)
        self.assertNotEquals(response.data['previous'], None)


    def test_drf2_list_view_query_filters(self):
        """
        Tests for Project Root view with filters. These basic tests are here
        because Project is the first API to use DRF2 and DRF2 hasn't been
        released yet. Not all DRF views need thorough integration testing like
        this.
        """

        # Tests that the phase filter works.
        request = factory.get(self.api_base + '?phase=fund')
        response = self.list_view(request).render()
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['count'], 13)
        self.assertEquals(len(response.data['results']), self.list_view_count)
        self.assertNotEquals(response.data['next'], None)
        self.assertEquals(response.data['previous'], None)

        # Tests that the next link works with a filter (this is also the last page).
        request = factory.get(response.data['next'])
        response = self.list_view(request).render()
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['count'], 13)
        self.assertEquals(len(response.data['results']), 13 % self.list_view_count)
        self.assertEquals(response.data['next'], None)
        self.assertNotEquals(response.data['previous'], None)

        # Tests that the previous link works with a filter.
        request = factory.get(response.data['previous'])
        response = self.list_view(request).render()
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data['count'], 13)
        self.assertEquals(len(response.data['results']), self.list_view_count)
        self.assertNotEquals(response.data['next'], None)
        self.assertEquals(response.data['previous'], None)


    def test_drf2_detail_view(self):
        """ Tests retrieving a project detail from the API. """

        # Get the list of projects.
        request = factory.get(self.api_base)
        response = self.list_view(request).render()
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        # Test retrieving the first project detail from the list.
        project = response.data['results'][0]
        request = factory.get(self.api_base + str(project['id']))
        response = self.detail_view(request, pk=project['id']).render()
        self.assertEquals(response.status_code, status.HTTP_200_OK)


class ProjectWallPostApiIntegrationTest(ProjectTestsMixin, UserTestsMixin, TestCase):
    """
    Integration tests for the Project Media WallPost API.
    """

    def setUp(self):
        self.some_project = self.create_project()
        self.another_project = self.create_project()
        self.some_user = self.create_user()
        self.project_wallposts_url = '/i18n/api/projects/wallposts/'
        self.project_media_wallposts_url = '/i18n/api/projects/mediawallposts/'
        self.project_text_wallposts_url = '/i18n/api/projects/textwallposts/'

        self.some_user = self.create_user()
        self.another_user = self.create_user()


    def test_project_media_wallpost_crud(self):
        """
        Tests for creating, retrieving, updating and deleting a Project Media WallPost.
        """
        self.client.login(username=self.some_project.owner.username, password='password')

        # Create a Project Media WallPost by Project Owner
        # Note: This test will fail when we require at least a video and/or a text but that's what we want.
        wallpost_title = 'This is my super project!'
        response = self.client.post(self.project_media_wallposts_url, {'title': wallpost_title, 'project_id': self.some_project.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['title'], wallpost_title)

        # Retrieve the created Project Media WallPost.
        project_wallpost_detail_url = "{0}{1}".format(self.project_media_wallposts_url, str(response.data['id']))
        response = self.client.get(project_wallpost_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['title'], wallpost_title)

        # Update the created Project Media WallPost by author.
        new_wallpost_title = 'This is my super-duper project!'
        response = self.client.put(project_wallpost_detail_url, {'title': new_wallpost_title, 'project_id': self.some_project.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['title'], new_wallpost_title)

        # Delete Project Media WallPost by author
        response = self.client.delete(project_wallpost_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response)

        # Create Project Media WallPost and retrieve by another user
        response = self.client.post(self.project_media_wallposts_url, {'title': wallpost_title, 'project_id': self.some_project.id})
        project_wallpost_detail_url = "{0}{1}".format(self.project_media_wallposts_url, str(response.data['id']))
        self.client.logout()
        self.client.login(username=self.some_user.username, password='password')
        response = self.client.get(project_wallpost_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['title'], wallpost_title)

        # Write Project Media WallPost by someone else then Project Owner should fail
        new_wallpost_title = 'This is not my project...'
        response = self.client.post(self.project_media_wallposts_url, {'title': new_wallpost_title, 'project_id': self.some_project.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

        # Write Project Media WallPost by Project Owner rto another Project should fail
        self.client.logout()
        self.client.login(username=self.some_project.owner.username, password='password')
        new_wallpost_title = 'This is not my project, although I do have a project'
        response = self.client.post(self.project_media_wallposts_url, {'title': new_wallpost_title, 'project_id': self.another_project.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

        # Update Project Media WallPost by someone else then Project Owner should fail
        second_wallpost_title = "My project rocks!"
        response = self.client.post(self.project_media_wallposts_url, {'title': second_wallpost_title, 'project_id': self.some_project.id})
        self.client.logout()
        self.client.login(username=self.some_user.username, password='password')
        response = self.client.put(project_wallpost_detail_url, {'title': new_wallpost_title, 'project_id': self.some_project.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

        # Retrieve a list of the two Project Media WallPosts that we've just added should work
        response = self.client.get(self.project_wallposts_url,  {'project_id': self.some_project.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['title'], second_wallpost_title)
        self.assertEqual(response.data['results'][1]['title'], wallpost_title)
        self.client.logout()

    def test_projecttextwallpost_crud(self):
        """
        Tests for creating, retrieving, updating and deleting wallposts
        """

        # Create text wallpost as not logged in guest should be denied
        text1 = 'Great job!'
        response = self.client.post(self.project_text_wallposts_url, {'text': text1, 'project_id': self.some_project.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

        self.client.login(username=self.some_user.username, password='password')

        # Create TextWallPost as a logged in member should be allowed
        response = self.client.post(self.project_text_wallposts_url, {'text': text1, 'project_id': self.some_project.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['text'], text1)

        # Retrieve text wallpost through WallPosts api
        wallpost_detail_url = "{0}{1}".format(self.project_wallposts_url, str(response.data['id']))
        response = self.client.get(wallpost_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['text'], text1)

        # Retrieve text wallpost through TextWallPosts api
        wallpost_detail_url = "{0}{1}".format(self.project_text_wallposts_url, str(response.data['id']))
        response = self.client.get(wallpost_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['text'], text1)

        self.client.logout()
        self.client.login(username=self.another_user.username, password='password')

        # Retrieve text wallpost through projectwallposts api by another user
        wallpost_detail_url = "{0}{1}".format(self.project_wallposts_url, str(response.data['id']))
        response = self.client.get(wallpost_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['text'], text1)

        # Create TextWallPost without a text should return an error
        response = self.client.post(self.project_text_wallposts_url, {'text': '', 'project_id': self.some_project.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertIsNotNone(response.data['text'])

        text2 = "I liek this project!"

        # Create TextWallPost as another logged in member should be allowed
        response = self.client.post(self.project_text_wallposts_url, {'text': text2, 'project_id': self.some_project.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['text'], text2)

        # Update TextWallPost by author is allowed
        text2a = 'I like this project!'
        wallpost_detail_url = "{0}{1}".format(self.project_text_wallposts_url, str(response.data['id']))
        response = self.client.put(wallpost_detail_url, {'text': text2a, 'project_id': self.some_project.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['text'], text2a)

        self.client.logout()
        self.client.login(username=self.some_user.username, password='password')

        # Update TextWallPost by another user (not the author) is allowed
        text2b = 'Mess this up!'
        wallpost_detail_url = "{0}{1}".format(self.project_text_wallposts_url, str(response.data['id']))
        response = self.client.put(wallpost_detail_url, {'text': text2b, 'project_id': self.some_project.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)


    def test_projectwallpost_list(self):
        """
        Tests for list and (soft)deleting wallposts
        """

        # Create a bunch of Project Text WallPosts
        self.client.login(username=self.some_user.username, password='password')
        for char in 'abcdefghijklmnopqrstuv':
            text = char * 15
            self.client.post(self.project_text_wallposts_url, {'text': text, 'project_id': self.some_project.id})

        self.client.logout()

        # And a bunch of Project Media WallPosts
        self.client.login(username=self.some_project.owner.username, password='password')
        for char in 'wxyz':
            title = char * 15
            self.client.post(self.project_media_wallposts_url, {'title': title, 'project_id': self.some_project.id})


        # Retrieve a list of the 26 Project WallPosts

        # View Project WallPost list works for author
        response = self.client.get(self.project_wallposts_url,  {'project_id': self.some_project.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(response.data['count'], 26)
        self.assertEqual(response.data['results'][0]['type'], 'media')
        self.assertEqual(response.data['results'][4]['type'], 'text')

        # Delete a Media WallPost and check that we can't retrieve it anymore
        project_wallpost_detail_url = "{0}{1}".format(self.project_media_wallposts_url, str(response.data['results'][0]['id']))
        response = self.client.delete(project_wallpost_detail_url)
        response = self.client.get(project_wallpost_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

        # WallPost List count should have decreased after deleting one
        response = self.client.get(self.project_wallposts_url,  {'project_id': self.some_project.id})
        self.assertEqual(response.data['count'], 25)

        # View Project WallPost list works for guest
        self.client.logout()
        response = self.client.get(self.project_wallposts_url,  {'project_id': self.some_project.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(response.data['count'], 25)



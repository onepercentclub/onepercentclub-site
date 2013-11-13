import json

from django.core import mail
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from bluebottle.bluebottle_utils.tests import UserTestsMixin

from apps.mail import send_mail
from apps.projects.tests import ProjectWallPostTestsMixin
from .models import Reaction


class WallPostReactionApiIntegrationTest(ProjectWallPostTestsMixin, TestCase):
    """
    Integration tests for the Project Media WallPost API.
    """

    def setUp(self):
        self.some_wallpost = self.create_project_text_wallpost()
        self.another_wallpost = self.create_project_text_wallpost()
        self.some_user = self.create_user()
        self.another_user = self.create_user()
        self.wallpost_reaction_url = '/api/wallposts/reactions/'
        self.project_text_wallpost_url = '/api/projects/wallposts/text/'


    def test_wallpost_reaction_crud(self):
        """
        Tests for creating, retrieving, updating and deleting a reaction to a Project WallPost.
        """

        # Create a Reaction
        self.client.login(email=self.some_user.email, password='password')
        reaction_text = "Hear! Hear!"
        response = self.client.post(self.wallpost_reaction_url,
                                    {'text': reaction_text, 'wallpost': self.some_wallpost.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(reaction_text in response.data['text'])

        # Retrieve the created Reaction
        reaction_detail_url = response.data['url']
        response = self.client.get(reaction_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTrue(reaction_text in response.data['text'])

        # Update the created Reaction by author.
        new_reaction_text = 'HEAR!!! HEAR!!!'
        response = self.client.put(reaction_detail_url, json.dumps({'text': new_reaction_text, 'wallpost': self.some_wallpost.id}), 'application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTrue(new_reaction_text in response.data['text'])

        # switch to another user
        self.client.logout()
        self.client.login(email=self.another_user.email, password='password')

        # Retrieve the created Reaction by non-author should work
        response = self.client.get(reaction_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTrue(new_reaction_text in response.data['text'])

        # Delete Reaction by non-author should not work
        self.client.logout()
        self.client.login(email=self.another_user.email, password='password')
        response = self.client.delete(reaction_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response)

        # Create a Reaction by another user
        another_reaction_text = "I'm not so sure..."
        response = self.client.post(self.wallpost_reaction_url,
                                    {'text': another_reaction_text, 'wallpost': self.some_wallpost.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        # Only check the substring because the single quote in "I'm" is escaped.
        # https://docs.djangoproject.com/en/dev/topics/templates/#automatic-html-escaping
        self.assertTrue('not so sure' in response.data['text'])

        # retrieve the list of Reactions for this WallPost should return two
        response = self.client.get(self.wallpost_reaction_url, {'wallpost': self.some_wallpost.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['count'], 2)
        self.assertTrue(new_reaction_text in response.data['results'][0]['text'])
        # Only check the substring because the single quote in "I'm" is escaped.
        # https://docs.djangoproject.com/en/dev/topics/templates/#automatic-html-escaping
        self.assertTrue('not so sure' in response.data['results'][1]['text'])

        # back to the author
        self.client.logout()
        self.client.login(email=self.some_user.email, password='password')

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
        self.client.login(email=self.some_user.email, password='password')
        reaction_text_1 = 'Great job!'
        response = self.client.post(self.wallpost_reaction_url,
                                    {'text': reaction_text_1, 'wallpost': self.some_wallpost.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(reaction_text_1 in response.data['text'])

        reaction_text_2 = 'This is a really nice post.'
        response = self.client.post(self.wallpost_reaction_url,
                                    {'text': reaction_text_2, 'wallpost': self.some_wallpost.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(reaction_text_2 in response.data['text'])


        # Check the size of the reaction list is correct.
        response = self.client.get(self.wallpost_reaction_url, {'wallpost': self.some_wallpost.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['count'], 2)

        # Check that the reaction listing without a wallpost id is working.
        response = self.client.get(self.wallpost_reaction_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['count'], 2)

        # Create a reaction on second blog post.
        reaction_text_3 = 'Super!'
        response = self.client.post(self.wallpost_reaction_url,
                                    {'text': reaction_text_3, 'wallpost': self.another_wallpost.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(reaction_text_3 in response.data['text'])
        # Save the detail url to be used in the authorization test below.
        second_reaction_detail_url = "{0}{1}".format(self.wallpost_reaction_url, response.data['id'])

        # Check that the size and data in the first reaction list is correct.
        response = self.client.get(self.wallpost_reaction_url, {'wallpost': self.some_wallpost.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['count'], 2)
        self.assertTrue(reaction_text_1 in response.data['results'][0]['text'])
        self.assertTrue(reaction_text_2 in response.data['results'][1]['text'])

        # Check that the size and data in the second reaction list is correct.
        response = self.client.get(self.wallpost_reaction_url, {'wallpost': self.another_wallpost.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['count'], 1)
        self.assertTrue(reaction_text_3 in response.data['results'][0]['text'])

        # Test that a reaction update from a user who is not the author is forbidden.
        self.client.logout()
        self.client.login(email=self.another_user.email, password='password')
        response = self.client.post(second_reaction_detail_url, {'text': 'Can I update this reaction?'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED, response.data)


    def test_embedded_reactions(self):
        """
            Test reactions embedded in Project WallPost Api calls
        """

        # Create two Reactions and retrieve the related Project Text WallPost should have the embedded
        self.client.login(email=self.some_user.email, password='password')
        reaction1_text = "Hear! Hear!"
        response = self.client.post(self.wallpost_reaction_url,
                                    {'text': reaction1_text, 'wallpost': self.some_wallpost.id})
        reaction1_detail_url = response.data['url']
        reaction2_text = "This is cool!"
        self.client.post(self.wallpost_reaction_url, {'text': reaction2_text, 'wallpost': self.some_wallpost.id})
        some_wallpost_detail_url = "{0}{1}".format(self.project_text_wallpost_url, str(self.some_wallpost.id))
        response = self.client.get(some_wallpost_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data['reactions']), 2)
        self.assertTrue(reaction1_text in response.data['reactions'][0]['text'])
        self.assertTrue(reaction2_text in response.data['reactions'][1]['text'])

        # Create a Reaction to another WallPost and retrieve that WallPost should return one embedded reaction
        reaction3_text = "That other post was way better..."
        self.client.post(self.wallpost_reaction_url, {'text': reaction3_text, 'wallpost': self.another_wallpost.id})
        another_wallpost_detail_url = "{0}{1}".format(self.project_text_wallpost_url, str(self.another_wallpost.id))
        response = self.client.get(another_wallpost_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data['reactions']), 1)
        self.assertTrue(reaction3_text in response.data['reactions'][0]['text'])

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


class WallPostApiRegressionTests(ProjectWallPostTestsMixin, UserTestsMixin, TestCase):
    """
    Integration tests for the Project Media WallPost API.
    """

    def setUp(self):
        self.user = self.create_user()
        self.wallpost = self.create_project_text_wallpost(author=self.user)

        self.project_media_wallposts_url = '/api/projects/wallposts/media/'
        self.project_text_wallposts_url = '/api/projects/wallposts/text/'
        self.project_wallposts_url = '/api/projects/wallposts/'
        self.wallpost_reaction_url = '/api/wallposts/reactions/'

    def test_html_javascript_propperly_escaped(self):
        """
        https://onepercentclub.atlassian.net/browse/BB-130
        """

        # Create a Reaction and check that the HTML is escaped.
        self.client.login(email=self.user.email, password='password')
        reaction_text = "<marquee>WOOOOOO</marquee>"
        # The paragraph tags are added by the linebreak filter.
        escaped_reaction_text = "<p>WOOOOOO</p>"
        response = self.client.post(self.wallpost_reaction_url, {'text': reaction_text, 'wallpost': self.wallpost.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(escaped_reaction_text, response.data['text'])

    def test_link_properly_created(self):
        """
        https://onepercentclub.atlassian.net/browse/BB-136
        """

        # Create a Reaction and check that the HTML link is properly created.
        self.client.login(email=self.user.email, password='password')
        reaction_text = "www.1procentclub.nl"
        # The paragraph tags and the anchor are added by the filters we're using.
        escaped_reaction_text = '<p><a target="_blank" href="http://www.1procentclub.nl" rel="nofollow">www.1procentclub.nl</a></p>'
        response = self.client.post(self.wallpost_reaction_url, {'text': reaction_text, 'wallpost': self.wallpost.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(escaped_reaction_text, response.data['text'])


class WallpostMailTests(ProjectWallPostTestsMixin, UserTestsMixin, TestCase):
    def setUp(self):
        self.user_a = self.create_user(email='a@example.com')
        self.user_b = self.create_user(email='b@example.com')
        self.user_c = self.create_user(email='c@example.com')

        self.project = self.create_project(owner=self.user_a)

    def test_translated_mail_subject(self):
        self.user_a.primary_language = 'en'
        self.user_a.save()

        send_mail(
            template_name='project_wallpost_reaction_new.mail',
            subject=_('Username'),
            obj=self.project,
            to=self.user_a,
            author=self.user_b
        )

        self.assertEqual(len(mail.outbox), 1)
        mail_message = mail.outbox[0]

        self.assertEquals(mail_message.subject, 'Username')

        self.user_a.primary_language = 'nl'
        self.user_a.save()

        send_mail(
            template_name='project_wallpost_reaction_new.mail',
            subject=_('Username'),
            obj=self.project,
            to=self.user_a,
            author=self.user_b
        )

        self.assertEqual(len(mail.outbox), 2)
        mail_message = mail.outbox[1]

        self.assertEquals(mail_message.subject, 'Gebruikersnaam')

    def test_new_wallpost_by_a_on_project_by_a(self):
        """
        Project by A + Wallpost by A => No mails.
        """
        # Object by A
        # |
        # +-- Wallpost by A (+)

        self.create_project_text_wallpost(project=self.project, author=self.user_a)

        # Mailbox should not contain anything.
        self.assertEqual(len(mail.outbox), 0)

    def test_new_wallpost_by_b_on_project_by_a(self):
        """
        Project by A + Wallpost by B => Mail to (project owner) A
        """
        # Object by A
        # |
        # +-- Wallpost by B (+)

        self.create_project_text_wallpost(project=self.project, author=self.user_b)

        # Mailbox should contain an email to project owner.
        self.assertEqual(len(mail.outbox), 1)
        m = mail.outbox[0]

        self.assertEqual(m.to, [self.user_a.email])

    def test_new_reaction_by_a_on_wallpost_a_on_project_by_a(self):
        """
        Project by A + Wallpost by A + Reaction by A => No mails.
        """
        # Object by A
        # |
        # +-- Wallpost by A
        # |   |
        # |   +-- Reaction by A (+)

        w = self.create_project_text_wallpost(project=self.project, author=self.user_a)

        # Empty outbox.
        mail.outbox = []
        Reaction.objects.create(text='Hello world', wallpost=w, author=self.user_a)

        # Mailbox should not contain anything.
        self.assertEqual(len(mail.outbox), 0)

    def test_new_reaction_by_b_on_wallpost_a_on_project_by_a(self):
        """
        Project by A + Wallpost by A + Reaction by B => Mail to (reaction author) A.
        """
        # Object by A
        # |
        # +-- Wallpost by A
        # |   |
        # |   +-- Reaction by A
        # |   |
        # |   +-- Reaction by B (+)

        w = self.create_project_text_wallpost(project=self.project, author=self.user_a)
        Reaction.objects.create(text='Hello world', wallpost=w, author=self.user_a)

        # Empty outbox.
        mail.outbox = []
        Reaction.objects.create(text='Hello world', wallpost=w, author=self.user_b)

        # Mailbox should contain an email to author of reaction a.
        self.assertEqual(len(mail.outbox), 1)
        m = mail.outbox[0]

        self.assertEqual(m.to, [self.user_a.email])

    def test_new_reaction_by_a_on_wallpost_b_on_project_by_a(self):
        """
        Project by A + Wallpost by B + Reaction by A => Mail to (reaction author) B.
        """
        # Object by A
        # |
        # +-- Wallpost by B
        #     |
        #     +-- Reaction by A (+)

        w = self.create_project_text_wallpost(project=self.project, author=self.user_b)

        # Empty outbox.
        mail.outbox = []
        Reaction.objects.create(text='Hello world', wallpost=w, author=self.user_a)

        # Mailbox should contain an email to author of reaction b.
        self.assertEqual(len(mail.outbox), 1)
        m = mail.outbox[0]

        self.assertEqual(m.to, [self.user_b.email])

    def test_new_reaction_by_b_on_wallpost_b_on_project_by_a(self):
        """
        Project by A + Wallpost by B + Reaction by B => Mail to (project owner) A.
        """
        # Object by A
        # |
        # +-- Wallpost by B
        #     |
        #     +-- Reaction by A
        #     |
        #     +-- Reaction by B (+)

        w = self.create_project_text_wallpost(project=self.project, author=self.user_b)
        Reaction.objects.create(text='Hello world', wallpost=w, author=self.user_a)

        # Empty outbox.
        mail.outbox = []
        Reaction.objects.create(text='Hello world', wallpost=w, author=self.user_b)

        # Mailbox should contain an email to project owner.
        self.assertEqual(len(mail.outbox), 1)
        m = mail.outbox[0]

        self.assertEqual(m.to, [self.user_a.email])

    def test_new_reaction_by_c_on_wallpost_b_on_project_by_a(self):
        """
        Project by A + Wallpost by B + Reaction by C => Mail to (project owner) A + Mail to (reaction author) B
        """
        # Object by A
        # |
        # +-- Wallpost by B
        #     |
        #     +-- Reaction by A
        #     |
        #     +-- Reaction by B
        #     |
        #     +-- Reaction by C (+)

        w = self.create_project_text_wallpost(project=self.project, author=self.user_b)
        Reaction.objects.create(text='Hello world', wallpost=w, author=self.user_a)
        Reaction.objects.create(text='Hello world', wallpost=w, author=self.user_b)

        # Empty outbox.
        mail.outbox = []
        Reaction.objects.create(text='Hello world', wallpost=w, author=self.user_c)

        # Mailbox should contain an email to project owner.
        self.assertEqual(len(mail.outbox), 2)
        m1 = mail.outbox[0]
        m2 = mail.outbox[1]

        self.assertListEqual([m2.to[0], m1.to[0]], [self.user_a.email, self.user_b.email])

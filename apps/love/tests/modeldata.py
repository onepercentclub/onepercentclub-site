"""
Tests for the love app concerning model data.
"""
from bluebottle.accounts.models import BlueBottleUser
from apps.love.models import LoveDeclaration
from bluebottle.bluebottle_utils.tests import CustomSettingsTestCase
from .models import TestBlogPost


class LoveTest(CustomSettingsTestCase):
    new_settings = dict(
        INSTALLED_APPS=(
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'apps.love',
            'apps.love.tests',
        )
    )


    @classmethod
    def setUpClass(cls):
        super(LoveTest, cls).setUpClass()

        # Define the basic database content to use.
        # This code runs before the transaction wrapper

        user1 = BlueBottleUser.objects.create_user('test1@example.com')
        user2 = BlueBottleUser.objects.create_user('test2@example.com')
        post1 = TestBlogPost.objects.create(title="Post 1", slug='post-1')
        post2 = TestBlogPost.objects.create(title="Post 2", slug='post-2')  # not loved as test
        post3 = TestBlogPost.objects.create(title="Post 3", slug='post-3')

        LoveDeclaration.objects.all().delete()


    def test_love(self):
        """
        Test whether love is spread nicely to the objects in the database.
        """
        # Set loves:
        # Post1: loved by user1 + user2
        # Post2: not loved
        # Post3: loved by user2 only
        user1 = BlueBottleUser.objects.get(email='test1@example.com')
        user2 = BlueBottleUser.objects.get(email='test2@example.com')
        post1 = TestBlogPost.objects.get(slug="post-1")
        post2 = TestBlogPost.objects.get(slug="post-2")
        post3 = TestBlogPost.objects.get(slug="post-3")

        # Assign via the object API
        post1.mark_as_loved(user1)
        post1.mark_as_loved(user2)
        post3.mark_as_loved(user2)

        # Could also be tested via the manager:
        #LoveDeclaration.objects.mark_as_loved(post1, user1)
        #LoveDeclaration.objects.mark_as_loved(post1, user2)
        #LoveDeclaration.objects.mark_as_loved(post3, user2)

        # Basic counting
        self.assertEquals(LoveDeclaration.objects.count(), 3, "expected 3 loves in the database now")
        self.assertEquals(LoveDeclaration.objects.for_object(post2).count(), 0, "expected no love for post-2")

        # Test via user dimension
        self.assertEquals(LoveDeclaration.objects.by_user(user1).count(), 1, "expected 1 love by user1")
        self.assertEquals(LoveDeclaration.objects.by_user(user2).count(), 2, "expected 2 loves by user2")

        # Test via object dimension
        self.assertEquals(sorted(LoveDeclaration.objects.for_object(post1).values_list('user__email', flat=True)), ['test1@example.com', 'test2@example.com'], "expected 2 love entries for post-1")
        self.assertEquals(sorted(LoveDeclaration.objects.for_object(post3).values_list('user__email', flat=True)), ['test2@example.com'], "expected 1 love entries for post-1")

        # Test reading loves via related field
        self.assertEqual(post1.loves.count(), 2)
        self.assertEqual(post2.loves.count(), 0)
        self.assertEqual(post3.loves.count(), 1)
        self.assertEqual(sorted(post1.loves.values_list('user__email', flat=True)), ['test1@example.com', 'test2@example.com'])

        # Test whether the query filter of the generic relation works
        self.assertEqual(sorted(TestBlogPost.objects.filter(loves__user=user2).values_list('slug', flat=True)), ['post-1', 'post-3'], "Expected query filter to work")

        # Test bulk methods
        all_blog_loves = LoveDeclaration.objects.for_objects(TestBlogPost.objects.all())
        self.assertEqual(all_blog_loves[post1.pk]['count'], 2)
        self.assertEqual(all_blog_loves[post3.pk]['count'], 1)

        # Test unloving, have 1 remaining
        post1.unmark_as_loved(user1)
        self.assertEquals(sorted(LoveDeclaration.objects.for_object(post1).values_list('user__email', flat=True)), ['test2@example.com'], "expected 1 love entries for post-1")


    def test_overwhelming_love(self):
        """
        Loving an object twice is nice but perhaps a bit too much for the database to handle.
        """
        user1 = BlueBottleUser.objects.get(email='test1@example.com')
        post1 = TestBlogPost.objects.get(slug="post-1")

        # Via object:
        post1.mark_as_loved(user1)
        post1.mark_as_loved(user1)  # This should be a no-op

        self.assertEqual(LoveDeclaration.objects.for_model(post1).by_user(user1).count(), 1, "Expected second love to be a no-op")
        self.assertEqual(post1.loves.by_user(user1).count(), 1, "Expected second love to be a no-op")


    def test_duplicate_unlove(self):
        """
        Unloving an object twice shouldn't hurt anyone.
        """
        user1 = BlueBottleUser.objects.get(email='test1@example.com')
        post1 = TestBlogPost.objects.get(slug="post-1")

        # Via object:
        post1.mark_as_loved(user1)
        post1.unmark_as_loved(user1)
        post1.unmark_as_loved(user1)

        self.assertEqual(post1.loves.by_user(user1).count(), 0, "Expected post1 to have 0 loves")

from django.test import TestCase

from .models import Organization


class OrganiationTestsMixin(object):
    """ Mixin base class for tests using organizations. """

    def create_organization(self):
        """
        Create a 'default' organization with some standard values so it can be
        saved to the database, but allow for overriding.

        The returned object is not yet saved to the database.
        """
        organization = Organization()

        return organization


class OrganizationTests(TestCase, OrganiationTestsMixin):
    """ Tests for organizations. """

    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

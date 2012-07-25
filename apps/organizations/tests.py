from django.test import TestCase

from .models import Organization


class OrganizationTestsMixin(object):
    """ Mixin base class for tests using organizations. """

    def create_organization(self):
        """
        Create a 'default' organization with some standard values so it can be
        saved to the database, but allow for overriding.

        The returned object is not yet saved to the database.
        """
        organization = Organization()

        return organization


class OrganizationTests(TestCase, OrganizationTestsMixin):
    """ Tests for organizations. """

    pass

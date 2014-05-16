from django.test import TestCase

from bluebottle.utils.tests import generate_random_slug

from .models import Organization


class OrganizationTestsMixin(object):
    """ Mixin base class for tests using organizations. """

    def create_organization(self, slug=None):
        """
        Create a 'default' organization with some standard values so it can be
        saved to the database, but allow for overriding.

        The returned object is not yet saved to the database.
        """
        if not slug:
            slug = generate_random_slug()
            while Organization.objects.filter(slug=slug).exists():
                 slug = generate_random_slug()

        organization = Organization(slug=slug)
        organization.save()
        return organization


class OrganizationTests(TestCase, OrganizationTestsMixin):
    """ Tests for organizations. """

    def test_save_unicode(self):
        """ Test save method and unicode representation."""
        organization = self.create_organization()

        unicode(organization)

        organization.save()

from django.test import TestCase

from apps.bluebottle_utils.tests import UserTestsMixin
from apps.organizations.tests import OrganiationTestsMixin

from .models import Project


class ProjectTestsMixin(OrganiationTestsMixin, UserTestsMixin):
    """ Mixin base class for tests using projects. """

    def create_project(self, organization=None, owner=None):
        """
        Create a 'default' project with some standard values so it can be
        saved to the database, but allow for overriding.

        The returned object is not yet saved to the database.
        """

        if not organization:
            organization = self.create_organization()
            organization.save()

        if not owner:
            # Create a new user with a random username
            owner = self.create_user()

        project = Project(organization=organization, owner=owner)

        return project


class ProjectTests(TestCase, ProjectTestsMixin):
    """ Tests for projcts. """

    pass

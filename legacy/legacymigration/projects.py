# coding=utf8

import logging
logger = logging.getLogger(__name__)

#from django.contrib.auth.models import User
#from django.contrib.auth import authenticate

from legacy.legacyprojects.models import Project as LegacyProject
from apps.projects.models import Project as NewProject

from .base import MigrateModel
from .utils import localize_datetime, crop_field


class MigrateProject(MigrateModel):
    """
    Migrate legacy projects to projects + phases.

    """

    def test_single(self, from_instance, to_instance):
        success = super(MigrateProject, self).test_single(from_instance, to_instance)
        return success

    def test_multiple(self, from_qs):
        # First, call the method from the superclass
        success = super(MigrateProject, self).test_multiple(from_qs)
        return success


    def list_from(self):
        qs = super(MigrateProject, self).list_from()

        # Include profile in query, speeding it up a bit
        qs.select_related('profile')

        return qs

    def migrate_single(self, from_instance, to_instance):
        super(MigrateProject, self).migrate_single(from_instance, to_instance)

        # Check whether this username already exists. If so, add a number
        counter = 1

        # Detect and change duplicate usernames
        qs = self.list_to()
        qs.exclude(pk=to_instance.pk)

    from_model = LegacyProject
    to_model = NewProject


    field_mapping = {
        'id': True, # True means just copy the field
        'title': True,
        'name': lambda i, f: {'slug': crop_field(i, f, 30)},
        'created': True,
        'organization': True,
        
        


        # Explcitly map stuff to /dev/null
        'weblog': None,
        

    
    }

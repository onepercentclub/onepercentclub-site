# coding=utf8

import logging
logger = logging.getLogger(__name__)

#from django.contrib.auth.models import User
#from django.contrib.auth import authenticate

from legacy.legacyorganizations.models import Organization as LegacyOrganization
from apps.organizations.models import Organization as NewOrganization

from .base import MigrateModel
from .utils import localize_datetime, crop_field


class MigrateOrganization(MigrateModel):
    """
    Migrate legacy projects to projects + phases.

    """

    def test_single(self, from_instance, to_instance):
        success = super(MigrateOrganization, self).test_single(from_instance, to_instance)
        return success

    def test_multiple(self, from_qs):
        # First, call the method from the superclass
        success = super(MigrateOrganization, self).test_multiple(from_qs)
        return success


    def list_from(self):
        qs = super(MigrateOrganization, self).list_from()

        # Include profile in query, speeding it up a bit
        qs.select_related('profile')

        return qs

    def migrate_single(self, from_instance, to_instance):
        super(MigrateOrganization, self).migrate_single(from_instance, to_instance)

        # Check whether this username already exists. If so, add a number
        counter = 1

        # Detect and change duplicate usernames
        qs = self.list_to()
        qs.exclude(pk=to_instance.pk)

    from_model = LegacyOrganization
    to_model = NewOrganization

    def migrate_name(instance, fieldname):
        """
        Migrate name to name and slug
        """
        name = getattr(instance, fieldname)
        slug = name.replace(' ','')[:100]
        return {'name': name, 'slug': slug}

    def migrate_website(instance, fieldname):
        """ Migrate website url """
        website = getattr(instance, fieldname)
        if website[:4] <> 'http':
            website = 'http://' . website
        return {'website': website}
            
    def migrate_deleted(instance, fieldname):
        """ Migrate deleted date """
        deleted = getattr(instance, fieldname)
        if deleted > '':
            deleted = localize_datetime(instance, fieldname)
        else:
            delete = None
        return {'deleted': deleted}
            

    field_mapping = {
        'id': True, # True means just copy the field
        'name': migrate_name,
        'description': True,
        'legal_status': True,
        'phonenumber': 'phone_number',
        'email': True,
        'website': migrate_website,

        'created': lambda i, f: {'created': localize_datetime(i, f)},
        'updated': lambda i, f: {'updated': localize_datetime(i, f)},
        'deleted': migrate_deleted,

        'partner_organizations': True,
        'account_bank_name': True,
        'account_bank_address': True,
        'account_bank_country': True,
        'account_iban': True,
        'account_bicswift': True,
        'account_number': True,
        'account_name': True,
        'account_city': True,

        


        # Explcitly map stuff to /dev/null
    
    }

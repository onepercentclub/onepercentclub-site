import logging
logger = logging.getLogger(__name__)

from legacy.legacyorganizations.models import (
    Organization as LegacyOrganization,
    OrganizationMember as LegacyOrganizationMember,
)

from apps.organizations.models import (
    Organization, OrganizationMember, OrganizationAddress
)

from .base import MigrateModel

from .mappings import (
    MappingMapping, EducateDateTimeMapping, SubstitutionMapping,
    NoneToStringMapping, OneToManyMapping, CountryMapping,
    NoneToStringCroppingMapping, IdentityMapping,
    WebsiteMapping, SlugifyCroppingMapping
)



class MigrateOrganization(MigrateModel):
    from_model = LegacyOrganization
    to_model = Organization

    def list_from(self):
        """ Filter out organizations with no name set. """
        qs = super(MigrateOrganization, self).list_from()

        # Exclude unnamed organizations
        qs = qs.exclude(name='')

        return qs

    field_mapping = {
        'id': True,
        'name': OneToManyMapping(
            IdentityMapping('title'),
            SlugifyCroppingMapping(100, to_field='slug', verbose=False)
        ),
        'legalstatus': 'legal_status',
        'phonenumber': NoneToStringMapping('phone_number'),
        'email': NoneToStringMapping(verbose=False),
        'website': WebsiteMapping(verbose=False),
        'description': NoneToStringMapping(),

        'created': EducateDateTimeMapping(verbose=False),
        # TODO
        # This one gets overridden by the current time and thus casues
        # errrors: find workaround
        # 'updated': EducateDateTimeMapping(verbose=False),
        'deleted': EducateDateTimeMapping(verbose=False),

        'partner_organisations': NoneToStringMapping(verbose=False),

        # Bank account details
        'account_number': True,
        'account_name': True,
        'account_city': True,
        'account_bank_name': NoneToStringMapping(verbose=False),
        'account_bank_address': NoneToStringMapping(verbose=False),

        # For now, don't map this until we have an actual FK on countries
        'account_bank_country_id': None,

        'account_iban': NoneToStringMapping(verbose=False),
        'account_bicswift': NoneToStringMapping(verbose=False),

        # Will be mapped through the address
        'street': None,
        'street_number': None,
        'postalcode': None,
        'city': None,
        'country_id': None,

        # Will be mapped through OrganizationMember
        'organizationmember': None,

        # Should be mapped later
        'referrals': None,

        # Should not be mapped from the reverse side
        'project': None
    }


class MigrateOrganizationMember(MigrateModel):
    from_model = LegacyOrganizationMember
    to_model = OrganizationMember

    def list_from(self):
        """ Only migrate members for migrated organizations. """
        qs = super(MigrateOrganizationMember, self).list_from()

        m = MigrateOrganization()
        organization_list = m.list_from()

        qs = qs.filter(org__in=organization_list)

        return qs

    def get_to_correspondence(self, other_object):
        """ Do correspondence by the member and organization id's. """

        return {
            'user_id': other_object.mem.id,
            'organization_id': other_object.org.id
        }

    def get_from_correspondence(self, other_object):
        """ Do correspondence by the member and organization id's. """

        return {
            'mem_id': other_object.user.id,
            'org_id': other_object.organization.id
        }

    field_mapping = {
        # This legacy table has no pk (!?)
        # 'id': True,

        'mem': None,
        'mem_id': 'user_id',

        'org': None,
        'org_id': 'organization_id'
    }
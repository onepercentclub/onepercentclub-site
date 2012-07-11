import logging
logger = logging.getLogger(__name__)

from legacy.legacymembers.models import Profile
from apps.accounts.models import UserProfile

from .base import MigrateModel

from .accounts import MigrateMemberAuth

from .mappings import (
    CropMapping, EducateDateTimeMapping, SubstitutionMapping, Mapping,
    NoneToStringMapping, MappingMapping, NoneToStringCroppingMapping
)


class WebsiteMapping(NoneToStringMapping):
    """
    Mapping for cleanup up website addresses.
    """
    def map_value(self, old_value):
        old_value = super(WebsiteMapping, self).map_value(old_value)

        old_value = old_value.strip()

        if old_value and old_value.startswith('//'):
            old_value = 'http:' + old_value

        if old_value and old_value.startswith('/'):
            old_value = 'http:/' + old_value

        return old_value


class MigrateProfile(MigrateModel):
    """
    Migrate from legacy profile to new UserProfile, using the member/user
    PK correspondence.
    """
    from_model = Profile
    to_model = UserProfile

    def get_to_correspondence(self, other_object):
        return {'user__pk': other_object.member.pk}

    def get_from_correspondence(self, other_object):
        return {'member__pk': other_object.user.pk}

    def list_from(self):
        qs = super(MigrateProfile, self).list_from()

        # Make sure we only migrate profiles for which the user is migrated
        # as well

        user_migrator = MigrateMemberAuth()
        member_set = user_migrator.list_from()

        qs = qs.filter(member__in=member_set)

        return qs

    field_mapping = {
        'member_id': 'user_id',
        'primary_language': 'interface_language',
        'newsletter': MappingMapping({
            'y': True
        }, default=False, verbose=False),
        'birthdate': True,
        'gender': MappingMapping({
            'm': 'male',
            'f': 'female',
        }, default=None, verbose=False),
        'location': NoneToStringMapping(verbose=False),
        'website': WebsiteMapping(verbose=False),
        'deleted': EducateDateTimeMapping(verbose=False),
        'about': NoneToStringMapping(verbose=False),
        'why': NoneToStringMapping(verbose=False),
        'contribution': NoneToStringMapping(verbose=False),

        # Warning: the next 2 should have verbose=True later
        'available_time': NoneToStringCroppingMapping(
            length=255, to_field='availability', verbose=False
        ),
        'working_location': NoneToStringCroppingMapping(255, verbose=False),

        # Stuff mapped to Django auth users
        'member': None,
        'firstname': None,
        'lastname': None,
        'created': None,

        # This will be used by the social auth application
        # (whatever it will be)
        'facebook_connect_enabled': None,
        'facebook_id': None
    }

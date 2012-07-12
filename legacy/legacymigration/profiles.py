import logging
logger = logging.getLogger(__name__)

from legacy.legacymembers.models import Profile
from apps.accounts.models import UserProfile, UserAddress

from .base import MigrateModel

from .accounts import MigrateMemberAuth

from .mappings import (
    EducateDateTimeMapping, NoneToStringCountryMapping, Mapping,
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

    def _get_members(self):
        """ Return all members to migrate. """

        user_migrator = MigrateMemberAuth()

        # Make sure we only fetch ID's from the database
        return user_migrator.list_from().only('id')

    def list_from(self):
        """
        Make sure we only migrate profiles for which the user is migrated
        as well.
        """

        qs = super(MigrateProfile, self).list_from()

        # Only migrate profiles for migrated members
        qs = qs.filter(member__in=self._get_members())

        return qs

    def _get_noprofile_member_pks(self):
        """
        In order to sort-of efficiently filter out members without a profile,
        use this caching helper function.
        """
        if not getattr(self, '_noprofile_member_pks', None):
            # Cache the values
            members = self._get_members()

            # Make a list of all members without a profile
            members = members.filter(profile=None)
            member_pks = members.values_list('id', flat=True).order_by('id')

            self._noprofile_member_pks = list(member_pks)

        return self._noprofile_member_pks

    def list_to(self):
        """
        Make sure only profiles that have a corresponding legacy profile are
        mapped back.
        """

        qs = super(MigrateProfile, self).list_to()

        # Exclude all the user/member id's for which no profile has been set.
        qs = qs.exclude(user__pk__in=self._get_noprofile_member_pks())

        return qs

    field_mapping = {
        # ID's do not correspond for profiles
        'id': None,

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
        'updated': None, # Warning: This one is not directly mapped to user

        # This will be used by the social auth application
        # (whatever it will be)
        'facebook_connect_enabled': None,
        'facebook_id': None,

        # Migrate to address
        'address': None,
        'zipcode': None,
        'city': None,
        'country': None,

        # Don't know what to do with these for now
        'authorize_capture': None,
        'billingcity': None,
        'billingname': None,
        'billingnumber': None,
        'recurring_donation_amount': None,

        # We will deal with file migrations later
        'photo': None
    }


class MemberMapping(Mapping):
    """ Set the target profile through the profile. """

    def map(self, instance, from_field):
        profile_mapper = MigrateProfile()
        to_profile = profile_mapper.get_to(instance)

        return {'user_profile': to_profile}

    def check(self, from_instance, to_instance, from_field):
        return from_instance == to_instance.user_profile


class MigrateUserAddress(MigrateProfile):
    """
    Migrate from Profile to UserAddres, respecting the member/user pk
    correspondence as with the profiles.
    """
    from_model = Profile
    to_model = UserAddress

    def get_to_correspondence(self, other_object):
        return {'user_profile__user__pk': other_object.member.pk}

    def get_from_correspondence(self, other_object):
        return {'member__pk': other_object.user_profile.user.pk}

    def list_to(self):
        """
        Make sure only profiles that have a corresponding legacy profile are
        mapped back.
        """
        qs = super(MigrateProfile, self).list_to()

        # Exclude all the user/member id's for which no profile has been set.
        qs = qs.exclude(
            user_profile__user__pk__in=self._get_noprofile_member_pks()
        )

        return qs

    field_mapping = {
        'member': MemberMapping(),

        'address': NoneToStringMapping('line1', verbose=False),
        'zipcode': NoneToStringMapping('zip_code', verbose=False),
        'city': NoneToStringMapping(verbose=False),
        'country': NoneToStringCountryMapping(verbose=False),

        # Dump all the other stuff
        'id': None,
        'member_id': None,
        'primary_language': None,
        'newsletter': None,
        'birthdate': None,
        'gender': None,
        'location': None,
        'website': None,
        'deleted': None,
        'about': None,
        'why': None,
        'contribution': None,
        'available_time': None,
        'working_location': None,
        'firstname': None,
        'lastname': None,
        'created': None,
        'updated': None,
        'facebook_connect_enabled': None,
        'facebook_id': None,
        'authorize_capture': None,
        'billingcity': None,
        'billingname': None,
        'billingnumber': None,
        'recurring_donation_amount': None,
        'photo': None

    }

# coding=utf8

import logging
logger = logging.getLogger(__name__)

from django.db.models import Q

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from legacy.legacymembers.models import Member

from .base import MigrateModel

from .mappings import (
    CropMapping, EducateDateTimeMapping, SubstitutionMapping, Mapping,
    NoneToStringCroppingMapping
)



class ActivatedMapping(Mapping):
    """
    Make sure that deleted users cannot login, as well as unactivated users.
    """
    def map(self, instance, from_field):
        activated = getattr(instance, from_field)

        deleted = instance.deleted

        # Deleted users should not be able to log in
        if deleted:
            activated = False

        return {'is_active': activated}

    def check(self, from_instance, to_instance, from_field):
        old_activated = getattr(from_instance, from_field)
        old_deleted = from_instance.deleted
        new_activated = to_instance.is_active

        return (not old_deleted and old_activated) is new_activated


class AdminMapping(Mapping):
    """
    1. admin = 1 should turn into is_superuser = TRUE (otherwise FALSE)
    2. admin > 0 should turn into is_staff = TRUE (otherwise FALSE)
    """

    def map(self, instance, from_field):
        admin = getattr(instance, from_field)

        if admin > 0:
            if admin == 1:
                return {
                    'is_superuser': True,
                    'is_staff': True
                }
            else:
                return {'is_staff': True}

        return {}

    def check(self, from_instance, to_instance, from_field):
        old_value = getattr(from_instance, from_field)

        superuser = to_instance.is_superuser
        staff = to_instance.is_staff

        return (superuser and staff and old_value == 1) or \
            (staff and old_value > 1) or \
            not (superuser or old_value)


class MigrateMemberAuth(MigrateModel):
    """
    Migrate legacy members to Django users.

    Spec:
        Field mapping
        id = mem_member.id
        username = mem_member.username
        firstname = mem_profile.first_name, see 5
        lastname  = mem_profile.last_name, see 5
        email = mem_members.email
        password = mem_members.password
        is_staff = see 2
        is_superuser = see 1
        last_login = mem_members.updated (don't think we actually have a
                     'lastlogin', this comes closest)
        date_joined = mem_members.created
    """

    def test_multiple(self, from_qs):
        """
        Test whether the login of just a few users actually works.
        """

        # First, call the method from the superclass
        success = super(MigrateMemberAuth, self).test_multiple(from_qs)

        # Now, test a bunch of users
        # (these users have been manually added for testing purposes)
        test_users = (
            # Activated user
            ('usermigrationtest2', 'pohji8'),

            # Activated user usermigrationtest2
            ('mathijs@visualspace.nl', 'pohji8'),

            # Thai, in Thai
            ('glavangadje', 'ภาษาไทย'),

            # Previous user glavangadje
            ('drbob@dokterbob.net', 'ภาษาไทย')
        )

        for user in test_users:
            logger.info('Attempting login for test user %s', user)

            if not authenticate(username=user[0], password=user[1]):
                logger.error(
                    "Test user '%s' could not login with password '%s'",
                    user[0], user[1]
                )
                success = False

        return success


    def list_from(self):
        """
        5. Some users don't have a mem_profile set, so they don't have a
        first/lastname. I set the username as first/lastname. We could leave
        them empty though.
        """
        qs = super(MigrateMemberAuth, self).list_from()

        # type_id = 2. Only migrate normal 'member' accounts.
        # Let's migrate 'organization', 'company' and 'school' accounts later.
        qs = qs.filter(type_id__gt=1)

        # Don't migrate users with username 'guest' and 'weg'.
        # Users 'weg' should be deleted at some point.
        # Users 'guest' should be turned into 'guest' users.
        # Marco and Edith have duplicate user names
        # We do not like them for that reason
        qs = qs.exclude(
            Q(username='guest') | Q(username='weg') | \
            Q(username='testaccountacceptemagverwijderd') |
            Q(username='edith') | Q(username='marco')
        )

        # Exclude all Loek's accounts that are not Loek himself
        qs = qs.exclude(
            Q(email='loek@1procentclub.nl') & ~Q(username='gannetson')
        )

        # Include profile in query, speeding it up a bit
        qs.select_related('profile')

        return qs

    from_model = Member
    to_model = User

    field_mapping = {
        'id': True, # True means just copy the field
        'email': CropMapping(75),

        'username': CropMapping(30),
        'profile': {
            'firstname': NoneToStringCroppingMapping(
                30, 'first_name', verbose=False),
            'lastname': NoneToStringCroppingMapping(
                30, 'last_name', verbose=False
            )
        },

        'password': SubstitutionMapping('legacy$%s', verbose=False),

        'created': EducateDateTimeMapping(
            tz=None, to_field='date_joined', verbose=False
        ),
        'updated': EducateDateTimeMapping(
            tz=None, to_field='last_login', verbose=False
        ),

        'admin': AdminMapping(),
        'activated':  ActivatedMapping(),

        # Explcitly map stuff to /dev/null
        'accepte_user': None,
        'activation': None,
        'alert': None,
        'batch': None,
        'deleted': None, # Mapped by migrate_activated
        'document': None,
        'donation': None,
        'ignore_activity': None,
        'invitee': None,
        'inviter': None,
        'language': None,
        'login': None,
        'membertag': None,
        'organizationmember': None,
        'passwordrequest': None,
        'paymentcluster': None,
        'portfolioline': None,
        'project': None,
        'project_message_set': None,
        'rating': None,
        'receiver': None,
        'reported': None,
        'sender': None,
        'task': None,
        'taskmember': None,
        'taskmessage': None,
        'testimonial': None,
        'type': None,
        'validated': None,
        'voucher': None,
        'weblog_message_set': None
    }

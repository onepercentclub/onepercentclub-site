# coding=utf8

import logging
logger = logging.getLogger(__name__)

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from legacy.legacymembers.models import Member

from .base import MigrateModel
from .utils import localize_datetime, crop_field


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
        last_login = mem_members.updated (don't think we actually have a 'lastlogin', this comes closest)
        date_joined = mem_members.created
    """

    def test_single(self, from_instance, to_instance):
        """
        There's members with username, firstname and/or lastname with more
        than 30 characters (default on auth_user). Until there is a clear
        mapping, this should cause at least the username to fail.
        """

        success = super(MigrateMemberAuth, self).test_single(from_instance, to_instance)


        # TODO: Test migration of activated

        if from_instance.username[:30] != to_instance.username:
            logger.error('No correspondence in username between %s and %s',
                repr(from_instance), repr(to_instance)
            )

            success = False

        if from_instance.email[:75] != to_instance.email:
            logger.error('No correspondence in email between %s and %s',
                repr(from_instance), repr(to_instance)
            )

            success = False

        if from_instance.profile:
            profile = from_instance.profile

            if profile.firstname and \
                profile.firstname[:30] != to_instance.first_name:

                logger.error('No correspondence in first name between %s and %s',
                    repr(from_instance), repr(to_instance)
                )

                success = False

            if profile.lastname and \
                from_instance.profile.lastname[:30] != to_instance.last_name:

                logger.error('No correspondence in last name between %s and %s',
                    repr(from_instance), repr(to_instance)
                )

                success = False

        return success

    def test_multiple(self, from_qs):
        """
        Test whether the login of just a few users actually works.
        """

        # First, call the method from the superclass
        success = super(MigrateMemberAuth, self).test_multiple(from_qs)

        # Now, test a bunch of users
        test_users = (
            ('usermigrationtest2', 'pohji8'), # Activated user
            ('mathijs@visualspace.nl', 'pohji8'), # Activated user usermigrationtest2
            ('glavangadje', 'ภาษาไทย'), # Thai, in Thai
            ('drbob@dokterbob.net', 'ภาษาไทย') # Previous user glavangadje
        )

        for user in test_users:
            if not authenticate(username=user[0], password=user[1]):
                logger.error("Test user '%s' could not login with password '%s'",
                    user[0], user[1]
                )
                success = False

        return success


    def list_from(self):
        """
        5. Some users don't have a mem_profile set, so they don't have a first/lastname. I set the username as first/lastname. We could leave them empty though.
        """
        qs = super(MigrateMemberAuth, self).list_from()

        # type_id = 2. Only migrate normal 'member' accounts.
        # Let's migrate 'organization', 'company' and 'school' accounts later.
        qs = qs.filter(type_id=2)

        # Don't migrate users with username 'guest' and 'weg'.
        # Users 'weg' should be deleted at some point.
        # Users 'guest' should be turned into 'guest' users.
        qs = qs.exclude(username='guest').exclude(username='weg')

        # Include profile in query, speeding it up a bit
        qs.select_related('profile')

        return qs

    def migrate_admin(instance, fieldname):
        """
        1. admin = 1 should turn into is_superuser = TRUE (otherwise FALSE)
        2. admin > 0 should turn into is_staff = TRUE (otherwise FALSE)
        """
        admin = getattr(instance, fieldname)

        if admin > 0:
            if admin == 1:
                return {'is_superuser': True}
            else:
                return {'is_staff': True}

        return {}

    def migrate_profile(instance, fieldname):
        """
        first_name = mem_profile.firstname, see 5
        last_name  = mem_profile.lastname, see 5
        """

        profile = getattr(instance, fieldname)

        if profile:
            return {
                'first_name': crop_field(profile, 'firstname', 30) or '',
                'last_name': crop_field(profile, 'lastname', 30) or ''
            }

        # Not every user has a profile, so don't worry
        return {}

    def migrate_single(self, from_instance, to_instance):
        super(MigrateMemberAuth, self).migrate_single(from_instance, to_instance)

        # Check whether this username already exists. If so, add a number
        counter = 1

        # Detect and change duplicate usernames
        qs = self.list_to()
        qs.exclude(pk=to_instance.pk)

        while qs.filter(username=to_instance.username).exists():
            to_instance.username = '%s%d' % (from_instance.username, counter)

            logger.warn('Duplicate username %s, changing to %s',
                from_instance.username, to_instance.username
            )

            counter += 1

    def migrate_activated(instance, fieldname):
        """
        Make sure that deleted users cannot login, as well as unactivated users.
        """
        activated = getattr(instance, fieldname)
        assert instance.activated == activated

        deleted = instance.deleted

        # Deleted users should not be able to log in
        if deleted:
            activated = False

        return {'is_active': activated}


    from_model = Member
    to_model = User

    field_mapping = {
        'id': True, # True means just copy the field
        'email': lambda i, f: {'email': crop_field(i, f, 75)},

        'username': lambda i, f: {'username': crop_field(i, f, 30)},
        'profile': migrate_profile,

        'password': lambda i, f: {'password': 'legacy$%s' % getattr(i, f)},
        # A function can be specified to yield a dictionary

        'created': lambda i, f: {'date_joined': localize_datetime(i, f)},
        'updated': lambda i, f: {'last_login': localize_datetime(i, f)},
        # A string can be passed to map to a different field

        'admin': migrate_admin,
        'activated':  migrate_activated,

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

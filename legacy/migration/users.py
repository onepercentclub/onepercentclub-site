from django.contrib.auth.models import User

from legacy.members.models import Member

from .base import MigrateModel


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
        assert from_instance.username == to_instance.username
        # assert from_instance.username[:30] == to_instance.username

        # assert from_instance.profile.first_name[:30] == to_instance.firstname
        # assert from_instance.profile.last_name[:30] == to_instance.lastname

    def list_from(self):
        """
        5. Some users don't have a mem_profile set, so they don't have a first/lastname. I set the username as first/lastname. We could leave them empty though.
        """
        qs = super(MigrateMemberAuth, self).super()

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

    @staticmethod
    def migrate_admin(admin):
        """
        1. admin = 1 should turn into is_superuser = TRUE (otherwise FALSE)
        2. admin > 0 should turn into is_staff = TRUE (otherwise FALSE)
        """
        if admin > 0:
            if admin == 1:
                return {'is_superuser': True}
            else:
                return {'is_staff': True}

        return {}

    @staticmethod
    def migrate_profile(profile):
        """
        firstname = mem_profile.first_name, see 5
        lastname  = mem_profile.last_name, see 5
        """
        return {
            'firstname': profile.first_name, #Should have[:30]
            'lastname': profile.last_name
        }

    from_model = Member
    to_model = User

    field_mapping = {
        'id': None, # None means just copy the field
        'email': None,

        'username': None, # This should become lambda x: x[:30]
        'profile': migrate_profile,

        'password': lambda p: {'password': p},
        # A function can be specified to yield a dictionary

        'created': 'date_joined',
        'updated': 'last_login',
        # A string can be passed to map to a different field

        'admin': migrate_admin
    }

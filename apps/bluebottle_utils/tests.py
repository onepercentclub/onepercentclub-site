import uuid

from django.contrib.auth.models import User


def generate_slug():
    return str(uuid.uuid4())[:30]


class UserTestsMixin(object):
    """ Mixin base class for tests requiring users. """

    def create_user(self, username=None, password=None):
        """ Create, save and return a new user. """

        # If username is set and not unique, it will raise a clearly
        # interpretable IntegrityError.
        # If auto-generated, make sure it's unique.

        if not username:
            username = generate_slug()
            while User.objects.filter(username=username).exists():
                 username = generate_slug()

        user = User.objects.create_user(username=username)

        return user

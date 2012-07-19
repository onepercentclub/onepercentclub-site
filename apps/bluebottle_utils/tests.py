import uuid

from django.contrib.auth.models import User


class UserTestsMixin(object):
    """ Mixin base class for tests requiring users. """

    def create_user(self, username=None, password=None):
        """ Create, save and return a new user. """

        if not username:
            # Generate a random username
            username = str(uuid.uuid4())[:30]

        user = User.objects.create_user(username=username)

        return user



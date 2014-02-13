from bluebottle.utils.models import Address
from django.db import models
from bluebottle.bb_accounts.models import BlueBottleBaseUser


class Member(BlueBottleBaseUser):

    address = models.ForeignKey('UserAddress')


class UserAddress(Address):
    pass

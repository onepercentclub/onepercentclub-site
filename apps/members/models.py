from django.db import models


from bluebottle.accounts.models import BlueBottleBaseUser

class OnepercentUser(BlueBottleBaseUser):

    class Meta:
        db_table = 'accounts_bluebottleuser'
        default_serializer = 'apps.members.serializers.UserProfileSerializer'





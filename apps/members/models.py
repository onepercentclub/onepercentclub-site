from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.utils.translation import ugettext as _
from bluebottle.bb_accounts.models import BlueBottleBaseUser
from bluebottle.utils.models import Address
from djchoices.choices import DjangoChoices, ChoiceItem
from django.conf import settings
from django.utils.translation import ugettext as _


class Member(BlueBottleBaseUser):

    #Create an address if none exists
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(Member, self).save(force_insert=False, force_update=False, using=None, update_fields=None)
        try:
            self.address
        except UserAddress.DoesNotExist:
            self.address = UserAddress.objects.create(user=self)
            self.address.save()


class UserAddress(Address):

    class AddressType(DjangoChoices):
        primary = ChoiceItem('primary', label=_("Primary"))
        secondary = ChoiceItem('secondary', label=_("Secondary"))

    address_type = models.CharField(_("address type"),max_length=10, blank=True, choices=AddressType.choices,
                                    default=AddressType.primary)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_("user"), related_name="address")

    class Meta:
        verbose_name = _("user address")
        verbose_name_plural = _("user addresses")
        #default_serializer = 'members.serializers.UserProfileSerializer'

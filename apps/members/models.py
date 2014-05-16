from django.db import models
from bluebottle.bb_accounts.models import BlueBottleBaseUser
from bluebottle.utils.models import Address
from djchoices.choices import DjangoChoices, ChoiceItem
from django.conf import settings
from django.utils.translation import ugettext as _


class Member(BlueBottleBaseUser):
    pass


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
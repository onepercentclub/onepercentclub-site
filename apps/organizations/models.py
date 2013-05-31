from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _

from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from django_iban.fields import IBANField, SWIFTBICField
from djchoices import DjangoChoices, ChoiceItem
from taggit_autocomplete_modified.managers import TaggableManagerAutocomplete as TaggableManager

from apps.bluebottle_utils.models import Address


class Organization(models.Model):
    """
    Organizations can run Projects.
    An organization has one or more members.
    """

    name = models.CharField(_("name"), max_length=255)
    slug = models.SlugField(_("slug"), max_length=100, unique=True)

    description = models.TextField(_("description"), blank=True)
    legal_status = models.TextField(_("legal status"), null=True, blank=True, help_text=_("The legal status of the organization (e.g. Foundation)."))
    phone_number = models.CharField(_("phone number"), max_length=255, blank=True)
    website = models.URLField(_("website"), max_length=255, blank=True)

    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("updated"))
    deleted = models.DateTimeField(_("deleted"), null=True, blank=True)

    partner_organizations = models.TextField(_("partner organizations"), blank=True)

    account_bank_name = models.CharField(_("account bank name"), max_length=255, blank=True)
    account_bank_address = models.CharField(_("account bank address"), max_length=255, blank=True)
    account_bank_country = models.ForeignKey('geo.Country', verbose_name=_("account bank country"), blank=True, null=True)
    account_iban = IBANField(_("account IBAN"), blank=True)
    account_bic = SWIFTBICField(_("account SWIFT-BIC"), blank=True)
    account_number = models.CharField(_("account number"), max_length=255, blank=True)
    account_name = models.CharField(_("account name"), max_length=255, blank=True)
    account_city = models.CharField(_("account city"), max_length=255, blank=True)
    account_other = models.CharField(_("account information that doesn't fit in the other field"), max_length=255, blank=True)

    tags = TaggableManager(blank=True, verbose_name=_("tags"))

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _("organization")
        verbose_name_plural = _("organizations")


class OrganizationMember(models.Model):
    """ Members from a Organization """

    class MemberFunctions(DjangoChoices):
        owner = ChoiceItem('owner', label=_("Owner"))
        editor = ChoiceItem('editor', label=_("Editor"))

    organization = models.ForeignKey(Organization, verbose_name=_("organization"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("user"))
    function = models.CharField(_("function"), max_length=20, choices=MemberFunctions.choices)

    class Meta:
        verbose_name = _("organization member")
        verbose_name_plural = _("organization members")


class OrganizationAddress(Address):
    """ Address model for Organizations. """

    class AddressType(DjangoChoices):
        physical = ChoiceItem('physical', label=_("Physical"))
        postal = ChoiceItem('postal', label=_("Postal"))
        other = ChoiceItem('other', label=_("Other"))

    type = models.CharField(_("type"), help_text=_("Address type."), max_length=8, blank=True, choices=AddressType.choices)
    organization = models.ForeignKey(Organization, verbose_name=_("organization"))

    class Meta:
        verbose_name = _("organization address")
        verbose_name_plural = _("organization addresses")

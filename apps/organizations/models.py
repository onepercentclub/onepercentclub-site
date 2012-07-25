from django.db import models
from django.utils.translation import ugettext as _

from django_countries import CountryField
from django_extensions.db.fields import (
    ModificationDateTimeField, CreationDateTimeField
)
from djchoices import DjangoChoices, ChoiceItem
from taggit.managers import TaggableManager

from apps.bluebottle_utils.models import Address


class Organization(models.Model):
    """
    Organizations can run Projects.
    An organization has one or more members.
    """

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100)

    description = models.TextField(blank=True)

    legal_status = models.TextField(null=True, blank=True,
                                    help_text="The legal status of the organization (e.g. Foundation)")

    phone_number = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)

    website = models.CharField(max_length=255, blank=True)

    created = CreationDateTimeField()
    updated = ModificationDateTimeField()
    deleted = models.DateTimeField(null=True, blank=True)

    partner_organisations = models.TextField(blank=True)

    account_bank_name = models.CharField(max_length=255, blank=True)
    account_bank_address = models.CharField(max_length=255, blank=True)
    account_bank_country = CountryField(blank=True)
    account_iban = models.CharField(max_length=255, blank=True)
    account_bicswift = models.CharField(max_length=255, blank=True)
    account_number = models.CharField(max_length=255, blank=True)
    account_name = models.CharField(max_length=255, blank=True)
    account_city = models.CharField(max_length=255, blank=True)

    tags = TaggableManager(blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']


class OrganizationMember(models.Model):
    """ Members from a Organization """

    class MemberFunctions(DjangoChoices):
        owner = ChoiceItem('owner', label=_("Owner"))
        admin = ChoiceItem('admin', label=_("Admin"))
        editor = ChoiceItem('editor', label=_("Editor"))
        member = ChoiceItem('member', label=_("Member"))

    organization = models.ForeignKey(Organization)
    user = models.ForeignKey('auth.User')
    function = models.CharField(max_length=20, choices=MemberFunctions.choices,
                                help_text="Function might determine Role later on.")


class OrganizationAddress(Address):
    """ Address model for Organizations. """

    class AddressType(DjangoChoices):
        physical = ChoiceItem('physical', label=_("Physical"))
        postal = ChoiceItem('postal', label=_("Postal"))
        other = ChoiceItem('other', label=_("Other"))

    type = models.CharField(max_length=8, blank=True, choices=AddressType.choices)
    organization = models.ForeignKey(Organization)

    class Meta:
        verbose_name_plural = "Organization Addresses"

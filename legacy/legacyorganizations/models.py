from django.db import models


class Organization(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    street = models.CharField(max_length=255, blank=True)
    street_number = models.CharField(max_length=255, blank=True)
    postalcode = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    legalstatus = models.TextField(blank=True)
    phonenumber = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    website = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    account_number = models.CharField(max_length=255, blank=True)
    account_name = models.CharField(max_length=255, blank=True)
    account_city = models.CharField(max_length=255, blank=True)
    country_id = models.IntegerField(null=True, blank=True)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    deleted = models.DateTimeField(null=True, blank=True)
    partner_organisations = models.CharField(max_length=255, blank=True)
    account_bank_name = models.CharField(max_length=255, blank=True)
    account_bank_address = models.CharField(max_length=255, blank=True)
    account_bank_country_id = models.IntegerField(null=True, blank=True)
    account_iban = models.CharField(max_length=255, blank=True)
    account_bicswift = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = u'org_organizations'
        managed = False

    def __unicode__(self):
        return self.name


class OrganizationMember(models.Model):
    org = models.ForeignKey(Organization)
    mem = models.ForeignKey('legacymembers.Member')

    class Meta:
        db_table = u'org_organizations_members'
        managed = False


class Referrals(models.Model):
    """ Rererrals (Referenten) """

    id = models.BigIntegerField(primary_key=True)
    org = models.ForeignKey(Organization)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    person_description = models.CharField(max_length=255)
    connection = models.CharField(max_length=255)

    class Meta:
        db_table = u'org_referrals'
        managed = False

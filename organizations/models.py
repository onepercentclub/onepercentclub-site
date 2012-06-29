from django.db import models

class Organization(models.Model):
    """ 
        Organizations can run Projects. 
        Organization has one or more members 
    """
    
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255, null=True)
    slug = models.CharField(max_length=255, null=True)
    street = models.CharField(max_length=255, null=True)
    street_number = models.CharField(max_length=255, null=True)
    postalcode = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    legalstatus = models.TextField(null=True)
    phonenumber = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=255, null=True)
    website = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    account_number = models.CharField(max_length=255, null=True)
    account_name = models.CharField(max_length=255, null=True)
    account_city = models.CharField(max_length=255, null=True)
    country_id = models.IntegerField(null=True)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    deleted = models.DateTimeField(null=True)
    partner_organisations = models.TextField(null=True)
    account_bank_name = models.CharField(max_length=255, null=True)
    account_bank_address = models.CharField(max_length=255, null=True)
    account_bank_country_id = models.IntegerField(null=True)
    account_iban = models.CharField(max_length=255, null=True)
    account_bicswift = models.CharField(max_length=255, null=True)
    
    def __unicode__(self):
        return self.title

    class Meta:
        ordering =  ['title']
    
    
class OrganizationMember(models.Model):
    """ Members from a Organization """
    STATUSES = (
        ('o', 'owner'),
        ('a', 'admin'),
        ('e', 'editor'),
        ('m', 'member'),
    )

    organization = models.ForeignKey(Organization)
    member = models.ForeignKey('auth.User')
    function = models.CharField(max_length=1, choices=STATUSES)
    """ Function might determine Role later on """
        

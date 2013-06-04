from django.db import models
from django_countries.fields import CountryField


class Address(models.Model):
    """
    A postal address.
    """
    line1 = models.CharField(max_length=100, blank=True)
    line2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = CountryField(blank=True)

    postal_code = models.CharField(max_length=20, blank=True)

    def __unicode__(self):
        return self.line1[:80]

    class Meta:
        abstract = True

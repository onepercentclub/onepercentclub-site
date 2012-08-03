from django.db import models


class Address(models.Model):
    """
    A postal address.
    """
    line1 = models.CharField(max_length=100, blank=True)
    line2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.ForeignKey('geo.Country', blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True)

    def __unicode__(self):
        return self.line1[:80]

    class Meta:
        abstract = True

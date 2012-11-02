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


try:
    from south.modelsinspector import add_ignored_fields
except ImportError:
    pass
else:
    # South should ignore the tags field as it's a RelatedField.
    add_ignored_fields((
        "^taggit_autocomplete_modified\.managers\.TaggableManagerAutocomplete",
    ))

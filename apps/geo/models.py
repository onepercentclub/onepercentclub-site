from django.db import models
from django.utils.translation import ugettext_lazy as _

from .validators import Alpha2CodeValidator, Alpha3CodeValidator, NumericCodeValidator


class GeoBaseModel(models.Model):
    '''
    Abstract base model for the UN M.49 geoscheme.
    Refs: http://unstats.un.org/unsd/methods/m49/m49.htm
          http://unstats.un.org/unsd/methods/m49/m49regin.htm
          https://en.wikipedia.org/wiki/United_Nations_geoscheme
          https://en.wikipedia.org/wiki/UN_M.49
    '''

    name = models.CharField(_("name"), max_length=100)
    # https://en.wikipedia.org/wiki/ISO_3166-1_numeric
    # http://unstats.un.org/unsd/methods/m49/m49alpha.htm
    numeric_code = models.CharField(_("numeric code"),
        max_length=3,unique=True,
        help_text=_("ISO 3166-1 or M.49 numeric code"),
        validators=[NumericCodeValidator]
    )

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True


class Region(GeoBaseModel):
    '''
    Macro geographical (continental) region as defined by the UN M.49
    geoscheme.
    '''

    class Meta(GeoBaseModel.Meta):
        ordering = ['name']
        verbose_name = _("region")
        verbose_name_plural = _("regions")


class SubRegion(GeoBaseModel):
    '''
    Geographical sub-region as defined by the UN M.49 geoscheme.
    '''

    region = models.ForeignKey(Region, verbose_name=_("region"))

    class Meta(GeoBaseModel.Meta):
        ordering = ['name']
        verbose_name = _("sub region")
        verbose_name_plural = _("sub regions")


class Country(GeoBaseModel):
    '''
    Geopolitical entity (country or territory) as defined by the UN M.49
    geoscheme.
    '''

    subregion = models.ForeignKey(SubRegion, verbose_name=_("sub region"))
    # https://en.wikipedia.org/wiki/ISO_3166-1
    alpha2_code = models.CharField(_("alpha2 code"), max_length=2, blank=True,
                                   help_text=_("ISO 3166-1 alpha-2 code"),
                                   validators=[Alpha2CodeValidator])
    alpha3_code = models.CharField(_("alpha3 code"), max_length=3, blank=True,
                                   help_text=_("ISO 3166-1 alpha-3 code"),
                                   validators=[Alpha3CodeValidator])
    # http://www.oecd.org/dac/aidstatistics/daclistofodarecipients.htm
    oda_recipient = models.BooleanField(_("ODA recipient"), default=False,
        help_text=_(
            "Whether a country is a recipient of Official Development"
            "Assistance from the OECD's Development Assistance Committee."
        )
    )

    class Meta(GeoBaseModel.Meta):
        ordering = ['name']
        verbose_name = _("country")
        verbose_name_plural = _("countries")

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import CreationDateTimeField


class Statistic(models.Model):
    """
    Stats for homepage
    """

    lives_changed = models.IntegerField()
    projects = models.IntegerField()
    countries = models.IntegerField()
    hours_spent = models.IntegerField()
    donated = models.IntegerField(verbose_name="Donated (obsolete)", help_text="Donated amount is calculated now. Hell yeah!")
    creation_date = CreationDateTimeField(_('creation date'))

    def __unicode__(self):
        return 'Site Statistics ' + str(self.creation_date)


from django.db import models

class Statistic(models.Model):
    """
    Stats for homepage
    """

    lives_changed = models.IntegerField()
    projects = models.IntegerField()
    countries = models.IntegerField()
    hours_spent = models.IntegerField()
    donated = models.IntegerField()

    def __unicode__(self):
        return 'Site Statistics ' + str(self.id)


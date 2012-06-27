'''
Created on May 24, 2012

@author: gannetson
'''
from django.db import models


class Continent(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    name_es = models.CharField(max_length=255, blank=True)
    name_en = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'sys_continents'


class Region(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    continent = models.ForeignKey(Continent)
    name_en = models.CharField(max_length=255, blank=True)
    name_es = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = u'sys_regions'

    def __unicode__(self):
        return self.name


class Country(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    region = models.ForeignKey(Region)
    dac = models.SmallIntegerField()
    latitude = models.CharField(max_length=20, blank=True)
    longitude = models.CharField(max_length=20, blank=True)
    number = models.CharField(max_length=3, blank=True)
    code2 = models.CharField(max_length=2, blank=True)
    code3 = models.CharField(max_length=3, blank=True)
    monetary_unit = models.CharField(max_length=50, blank=True)
    monetary_code = models.CharField(max_length=3, blank=True)

    class Meta:
        db_table = u'sys_countries'

    def __unicode__(self):
        return self.name

    def location(self):
        return self.name + ' - ' + self.region.name


class Tag(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    count = models.IntegerField()

    class Meta:
        db_table = u'sys_tags'


class Log(models.Model):
    """ Loging. Mainly (only?) logs payment processes
        from cron jobs and custom scripts (from cron dir) """

    id = models.BigIntegerField(primary_key=True)
    level = models.IntegerField()
    time = models.DateTimeField()
    system = models.CharField(max_length=255)
    subsystem = models.CharField(max_length=255)
    file = models.CharField(max_length=255)
    line = models.IntegerField()
    session = models.IntegerField()
    message = models.TextField()

    class Meta:
        db_table = u'sys_log'


class GoogleApiKey(models.Model):
    """ Not needed anymore since Gmap v3 """
    """ GooleApiKeys for GoogleMaps. """

    domain = models.CharField(max_length=255, primary_key=True)
    key = models.CharField(max_length=255)

    class Meta:
        db_table = u'sys_google_api_keys'


class Login(models.Model):
    """ Loging for Member logins.
        We want to track if someone is online,
        but I guess there's a better place for it """

    member = models.ForeignKey('members.Member')
    created = models.DateTimeField()

    class Meta:
        db_table = u'sys_logins'


class Session(models.Model):
    """ Track phpsessions ?? """
    """ Not sure if phpsessions are stored on disk as well """

    id = models.CharField(max_length=32, primary_key=True)
    created = models.DateTimeField()
    data = models.TextField() # This field type is a guess.
    modified = models.DateTimeField()

    class Meta:
        db_table = u'sys_sessions'


class Site(models.Model):
    """ Looks this isn't realy used """

    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    locale = models.CharField(max_length=5)
    template = models.CharField(max_length=255)

    class Meta:
        db_table = u'sys_sites'



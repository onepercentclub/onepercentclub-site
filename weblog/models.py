from django.db import models
from members.models import Member

# Create your models here.

class Weblog(models.Model):
    """ A weblog. Typicaly connected to a Project """ 
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created = models.DateTimeField()
    class Meta:
        db_table = u'web_weblog'

class Message(models.Model):
    """ A post in a Weblog """
    id = models.IntegerField(primary_key=True)
    weblog = models.ForeignKey(Weblog)
    member = models.ForeignKey(Member)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created = models.DateTimeField()
    class Meta:
        db_table = u'web_weblog_message'

        

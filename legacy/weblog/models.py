from django.db import models


class Weblog(models.Model):
    """ A weblog. Typicaly connected to a Project """

    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created = models.DateTimeField()

    class Meta:
        db_table = u'web_weblog'
        managed = False


class Message(models.Model):
    """ A post in a Weblog """

    id = models.IntegerField(primary_key=True)
    weblog = models.ForeignKey(Weblog)
    member = models.ForeignKey('members.Member',
        related_name='weblog_message_set'
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    created = models.DateTimeField()

    class Meta:
        db_table = u'web_weblog_message'
        managed = False

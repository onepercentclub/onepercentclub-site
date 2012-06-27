from django.db import models


class Action(models.Model):
    """ Actions (eg 24H Actions) """

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    project = models.ForeignKey('projects.Project', null=True, blank=True)
    title = models.CharField(max_length=255, blank=True)
    slogan = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    story = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    deadline = models.CharField(max_length=255, blank=True)
    create_date = models.DateTimeField()
    picture = models.CharField(max_length=255, blank=True)
    group_picture = models.CharField(max_length=255, blank=True)
    group_text = models.TextField(blank=True)
    active = models.NullBooleanField(null=True, blank=True)

    class Meta:
        db_table = u'act_action'
        managed = False

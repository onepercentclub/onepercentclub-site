from django.db import models


class Expertise(models.Model):
    """ Expertises used to connect Tasks """

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    name_en = models.CharField(max_length=255, blank=True)
    name_es = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = u'expertises'
        managed = False

    def __unicode__(self):
        return self.name_en


class TaskExpertise(models.Model):
    """ Expertise for a ProjectTask """

    id = models.IntegerField(primary_key=True)
    task = models.ForeignKey('Task')
    expertise = models.ForeignKey(Expertise)

    class Meta:
        db_table = u'prj_project_tasks_expertises'
        managed = False


class TaskMember(models.Model):
    task = models.ForeignKey('Task')
    member = models.ForeignKey('legacymembers.Member')
    status = models.IntegerField(null=True, blank=True)
    comment = models.TextField(blank=True)
    recommendation_rating = models.IntegerField(null=True, blank=True)
    recommendation_text = models.TextField(blank=True)

    class Meta:
        db_table = u'prj_project_task_members'
        managed = False


class Task(models.Model):
    """ 1%TASK. Conected to a Project """

    id = models.IntegerField(primary_key=True)
    project = models.ForeignKey('legacyprojects.Project', null=True, blank=True)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    description_short = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=255)
    deadline = models.CharField(max_length=255, blank=True)
    estimated_time = models.CharField(max_length=255, blank=True)
    create_date = models.DateTimeField()
    photo = models.CharField(max_length=255, blank=True)
    expertises = models.ManyToManyField(Expertise, through=TaskExpertise)
    members = models.ManyToManyField('legacymembers.Member', through=TaskMember)
    tags = models.ManyToManyField('Tag', through='TaskTag')

    class Meta:
        db_table = u'prj_project_tasks'
        managed = False


class Tag(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    count = models.IntegerField()

    class Meta:
        db_table = u'sys_task_tags'
        managed = False


class TaskTag(models.Model):
    task = models.ForeignKey(Task)
    tag = models.ForeignKey(Tag)

    class Meta:
        db_table = u'prj_project_tasks_tags'
        managed = False


class Document(models.Model):
    """
    ProjectDocument.
    A document that is linked to a Project. Or in this case to as ProjectTask.
    """
    id = models.IntegerField(primary_key=True)
    project = models.ForeignKey('legacyprojects.Project', null=True, blank=True)
    title = models.CharField(max_length=255, blank=True)
    filename = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    create_date = models.DateTimeField()
    member = models.ForeignKey('legacymembers.Member', null=True, blank=True)
    task = models.ForeignKey(Task, null=True, blank=True)
    doc_type = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = u'prj_project_documents'
        managed = False


class TaskMessage(models.Model):
    id = models.IntegerField(primary_key=True)
    task = models.ForeignKey(Task)
    member = models.ForeignKey('legacymembers.Member')
    text = models.TextField()
    created = models.DateTimeField()
    deleted = models.DateTimeField(null=True, blank=True)
    document_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = u'task_messages'
        managed = False

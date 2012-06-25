from django.db import models


class Folder(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    deletable = models.IntegerField()
    project = models.ForeignKey('projects.Project', null=True, blank=True)
    status = models.CharField(max_length=255)

    class Meta:
        db_table = u'flm_folders'


class File(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    # Note: file is a reserved name and *might* cause trouble
    file = models.CharField(max_length=50)
    folder = models.ForeignKey(Folder)
    created = models.DateTimeField()
    updated = models.DateTimeField()

    class Meta:
        db_table = u'flm_files'

    def smallUrl(self):
        return 'http://www.1procentclub.nl/cache/65x50_fit/' + self.file

    def url(self):
        return 'http://www.1procentclub.nl/cache/640x480_fit/' + self.file

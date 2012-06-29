from django.db import models


class Catalog(models.Model):
    """ A catalog holds Albums. Every Project has a reference to a Catalog """
    id = models.IntegerField(primary_key=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = u'alb_catalogs'
        managed = False


class Album(models.Model):
    """ Album. An album holds Pictures """

    id = models.IntegerField(primary_key=True)
    catalog = models.ForeignKey(Catalog)
    folder = models.ForeignKey('legacyfilemanager.Folder')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created = models.DateTimeField()
    updated = models.DateTimeField()

    class Meta:
        db_table = u'alb_albums'
        managed = False

    def pictures(self):
        return self.picture_set.select_related(depth=1).all()


class Picture(models.Model):
    """ Has info about a picture. The file is legacyfilemanager.models.File """

    id = models.IntegerField(primary_key=True)
    album = models.ForeignKey(Album)
    file = models.ForeignKey('legacyfilemanager.File')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    views = models.IntegerField()
    project = models.ForeignKey('legacyprojects.Project')

    class Meta:
        db_table = u'alb_fotos'
        managed = False


from django.db import models

""" Some intricate way of storing legacycms pages """

class InnerTemplate(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    contents = models.TextField()
    created = models.DateTimeField()
    updated = models.DateTimeField()

    class Meta:
        db_table = u'cms_inner_templates'
        managed = False


class Page(models.Model):
    id = models.IntegerField(primary_key=True)
    template = models.ForeignKey(InnerTemplate)
    slug = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    startdate = models.DateTimeField(null=True, blank=True)
    enddate = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    headtitle = models.CharField(max_length=255, blank=True)
    metakeywords = models.CharField(max_length=255, blank=True)
    metadescription = models.TextField(blank=True)
    language = models.CharField(max_length=6, blank=True)

    class Meta:
        db_table = u'cms_pages'
        managed = False


class Block(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    internal_url = models.CharField(max_length=255)

    class Meta:
        db_table = u'blk_blocks'
        managed = False


class Configuration(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    meta = models.CharField(max_length=255, blank=True)
    block = models.ForeignKey(Block)
    default_value = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = u'blk_configurations'
        managed = False


class PageBlock(models.Model):
    id = models.IntegerField(primary_key=True)
    page = models.ForeignKey(Page)
    block = models.ForeignKey(Block)
    placeholder = models.CharField(max_length=255)
    ordering = models.IntegerField()

    class Meta:
        db_table = u'blk_page_blocks'
        managed = False


class PageConfiguration(models.Model):
    id = models.IntegerField(primary_key=True)
    page_block = models.ForeignKey(PageBlock)
    configuration = models.ForeignKey(Configuration)
    value = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = u'blk_pages_configurations'
        managed = False



from django.db import models


class Item(models.Model):
    """ News item """

    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    type = models.CharField(max_length=100)
    ordering = models.IntegerField(null=True, blank=True)
    author = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    language_code = models.CharField(max_length=6, blank=True)

    class Meta:
        db_table = u'nws_news'

    def date(self):
        return self.created

    def html(self):
        html = self.content
        html = html.replace('http://www.1procentclub.nl/doen/task?id=', '/tasks/view/')
        html = html.replace('http://www.1procentclub.nl/projects/search/', '/projects/search/')
        html = html.replace('http://www.1procentclub.nl/projects/', '/projects/view/')
        html = html.replace('/assets', 'http://1procentclub.nl/assets')
        return html
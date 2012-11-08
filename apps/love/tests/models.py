from django.db import models
from apps.love.models import LovableModel


class TestBlogPost(LovableModel):
    """
    A model that is used for testing.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField()

    def __unicode__(self):
        return self.title

